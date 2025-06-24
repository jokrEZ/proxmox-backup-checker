import glob
import json
import os
from datetime import datetime, timedelta

import requests
from proxmoxer import ProxmoxAPI

CONFIG_PATH = os.getenv("CONFIG_PATH", "config.json")


def load_config():
    """Lädt die Konfiguration aus einer JSON-Datei."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der Konfiguration: {e}")
        exit(1)


def get_proxmox_connection(config):
    """Stellt die Verbindung zur Proxmox API her (nur API-Token erlaubt, neues Format)."""
    user = config.get("proxmox_api_token_user")
    token_name = config.get("proxmox_api_token_name")
    token_secret = config.get("proxmox_api_token_secret")

    if user and token_name and token_secret:
        try:
            return ProxmoxAPI(
                config["proxmox_host"],
                user=user,
                token_name=token_name,
                token_value=token_secret,
                verify_ssl=config.get("proxmox_verify_ssl", False),
                backend="https",
            )
        except Exception as e:
            print(f"Fehler bei der Anmeldung mit API-Token: {e}")
            exit(1)
    else:
        print(
            "Fehler: Es wurden keine gültigen API-Token-Zugangsdaten für die Proxmox API gefunden. Bitte prüfe die config.json und gib einen API-Token an."
        )
        exit(1)


def get_backup_jobs(proxmox):
    """Liest die Backupregeln (Jobs) aus der Proxmox API aus."""
    return proxmox.cluster.backup.get()


def get_last_scheduled_datetime(now, dow_list, starttime):
    """Berechnet das letzte geplante Ausführungsdatum für einen Job anhand von dow und starttime."""
    weekday_map = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
    stunden, minuten = map(int, starttime.split(":"))
    # Finde alle Wochentage als Index (0=sonntag, 6=samstag)
    dow_indices = [weekday_map.index(d) for d in dow_list if d in weekday_map]
    # Suche rückwärts ab heute
    for tage_zurueck in range(0, 8):
        tag = (now.weekday() - tage_zurueck) % 7
        # Python: 0=Montag, Proxmox: 0=Sonntag
        proxmox_tag = (tag + 1) % 7  # 0=Sonntag
        if proxmox_tag in dow_indices:
            dt = (now - timedelta(days=tage_zurueck)).replace(
                hour=stunden, minute=minuten, second=0, microsecond=0
            )
            if dt <= now:
                return dt
    return None


def get_next_scheduled_datetime(now, dow_list, starttime):
    """Berechnet das nächste geplante Ausführungsdatum für einen Job anhand von dow und starttime."""
    weekday_map = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
    stunden, minuten = map(int, starttime.split(":"))
    dow_indices = [weekday_map.index(d) for d in dow_list if d in weekday_map]
    for tage_voraus in range(0, 8):
        tag = (now.weekday() + tage_voraus) % 7
        proxmox_tag = (tag + 1) % 7  # 0=Sonntag
        if proxmox_tag in dow_indices:
            dt = (now + timedelta(days=tage_voraus)).replace(
                hour=stunden, minute=minuten, second=0, microsecond=0
            )
            if dt > now:
                return dt
    return None


def parse_schedule(schedule_str):
    """Parst das Proxmox schedule-Format (z.B. 'sun 01:00' oder '03:00')."""
    if not schedule_str:
        return ["mon", "tue", "wed", "thu", "fri", "sat", "sun"], "00:00"

    parts = schedule_str.strip().split()
    if len(parts) == 2:
        # Format: 'sun 01:00'
        dow, time = parts
        return [dow], time
    elif len(parts) == 1:
        # Format: '03:00' (täglich)
        time = parts[0]
        return ["mon", "tue", "wed", "thu", "fri", "sat", "sun"], time
    else:
        # Fallback
        return ["mon", "tue", "wed", "thu", "fri", "sat", "sun"], "00:00"


def get_vm_names(proxmox):
    """Holt die Namen aller VMs und Container von der Proxmox API."""
    vm_names = {}
    try:
        # Hole alle VMs (qemu)
        vms = proxmox.cluster.resources.get(type="vm")
        for vm in vms:
            vm_names[str(vm["vmid"])] = vm.get("name", f"VM-{vm['vmid']}")
    except Exception as e:
        print(f"Fehler beim Abrufen der VM-Namen: {e}")
    return vm_names


def analyze_backup_logs(jobs, log_dir, vm_names, debug=False):
    """Analysiert die Backuplogs entsprechend der geplanten Jobs und gibt Debug-Infos aus."""
    fehlerhafte_backups = []
    erfolgreiche_backups = []
    letzte_backups = {}
    now = datetime.now()
    weekday_map = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]

    # Sammle alle VM/CT-IDs aus allen Jobs (auch inaktive)
    alle_vmids = set()
    job_info = {}  # vmid -> (job_id, dow_list, starttime, enabled)

    for job in jobs:
        enabled = job.get("enabled", 1)
        schedule = job.get("schedule", "00:00")
        dow_list, starttime = parse_schedule(schedule)
        job_id = job.get("id", "unbekannt")

        if debug:
            print(
                f"[DEBUG] Job {job_id}: enabled={enabled}, schedule='{schedule}' -> dow={dow_list}, starttime='{starttime}', vmids={job.get('vmid') or job.get('vmids')}"
            )

        vmids = job.get("vmid") or job.get("vmids") or []
        if isinstance(vmids, str):
            vmids = [v.strip() for v in vmids.split(",") if v.strip()]
        elif isinstance(vmids, int):
            vmids = [str(vmids)]

        for vmid in vmids:
            alle_vmids.add(vmid)
            job_info[vmid] = (job_id, dow_list, starttime, enabled)

    if debug:
        print(f"\n[DEBUG] Gefundene VM/CT-IDs in Jobs: {sorted(alle_vmids)}")

    # Prüfe jede VM/CT einzeln
    for vmid in alle_vmids:
        job_id, dow_list, starttime, enabled = job_info[vmid]

        if not enabled:
            if debug:
                print(f"[DEBUG] VM/CT {vmid} - Job ist deaktiviert")
            continue

        if debug:
            print(
                f"[DEBUG] VM/CT {vmid} - Job-Parameter: dow={dow_list}, starttime={starttime}"
            )

        # Berechne letzten geplanten Ausführungstermin
        last_scheduled = get_last_scheduled_datetime(now, dow_list, starttime)

        if debug:
            print(f"[DEBUG] VM/CT {vmid} - Letzter geplanter Termin: {last_scheduled}")

        # Suche Logfiles für diese VM/CT
        log_path_lxc = os.path.join(log_dir, f"lxc-{vmid}.log")
        log_path_qemu = os.path.join(log_dir, f"qemu-{vmid}.log")

        logfiles = []
        if os.path.exists(log_path_lxc):
            logfiles.append(
                (log_path_lxc, datetime.fromtimestamp(os.path.getmtime(log_path_lxc)))
            )
        if os.path.exists(log_path_qemu):
            logfiles.append(
                (log_path_qemu, datetime.fromtimestamp(os.path.getmtime(log_path_qemu)))
            )

        if not logfiles:
            fehlerhafte_backups.append((vmid, "Logdatei nicht gefunden"))
            continue

        # Nimm das aktuellste Logfile
        best_log, best_mtime = max(logfiles, key=lambda x: x[1])

        # Prüfe Loginhalt
        with open(best_log, "r", encoding="utf-8") as log_file:
            log_content = log_file.read()
            hat_fehler = any(
                err in log_content for err in ["ERROR", "FAILED", "aborted"]
            )

        # Speichere für allgemeine Übersicht
        if not hat_fehler:
            letzte_backups[vmid] = (best_mtime, best_log)

        # Prüfe, ob Logfile aktuell genug ist
        if last_scheduled and best_mtime < last_scheduled:
            fehlerhafte_backups.append(
                (
                    vmid,
                    f"Logdatei ist zu alt (letzte Änderung: {best_mtime}, erwartet: nach {last_scheduled})",
                )
            )
        elif hat_fehler:
            fehlerhafte_backups.append(
                (vmid, f"Fehler im Log gefunden ({os.path.basename(best_log)})")
            )
        else:
            erfolgreiche_backups.append(
                (
                    vmid,
                    f"Backup erfolgreich am {best_mtime} ({os.path.basename(best_log)})",
                )
            )

    if debug:
        print("\n[DEBUG] Letzte erfolgreiche Backups (unabhängig vom Zeitplan):")
        for vmid, (mtime, logfile) in letzte_backups.items():
            vm_name = vm_names.get(vmid, f"VM-{vmid}")
            print(
                f"  - VM/CT-ID: {vmid} ({vm_name}): {mtime} ({os.path.basename(logfile)})"
            )
        print("\n[DEBUG] Erfolgreiche Backups (nach Zeitplan):")
        for vmid, info in erfolgreiche_backups:
            vm_name = vm_names.get(vmid, f"VM-{vmid}")
            print(f"  - VM/CT-ID: {vmid} ({vm_name}): {info}")
        print("\n[DEBUG] Fehlerhafte Backups:")
        for vmid, fehler in fehlerhafte_backups:
            vm_name = vm_names.get(vmid, f"VM-{vmid}")
            print(f"  - VM/CT-ID: {vmid} ({vm_name}): {fehler}")
        print("\n[DEBUG] Gefundene Logdateien im Logverzeichnis:")
        all_logs = glob.glob(os.path.join(log_dir, "*.log"))
        for log in sorted(all_logs):
            print(f"  - {os.path.basename(log)}")
    return fehlerhafte_backups, vm_names


def send_ha_notification(message, webhook_url):
    """Sendet eine Benachrichtigung an Home Assistant via Webhook."""
    data = {"message": message}
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"Fehler beim Senden der Benachrichtigung: {e}")


def main():
    config = load_config()
    proxmox = get_proxmox_connection(config)
    log_dir = config.get("log_dir", "/var/log/vzdump")
    jobs = get_backup_jobs(proxmox)
    vm_names = get_vm_names(proxmox)
    debug = config.get("debug", False)
    if debug:
        print("\n[DEBUG] Starte Analyse der Backup-Jobs...")
    fehlerhafte_backups, _ = analyze_backup_logs(jobs, log_dir, vm_names, debug=debug)
    if fehlerhafte_backups:
        for vmid, fehler in fehlerhafte_backups:
            vm_name = vm_names.get(vmid, f"VM-{vmid}")
            nachricht = f"Backup-Fehler bei {vm_name} (ID: {vmid}): {fehler}"
            send_ha_notification(nachricht, config["ha_webhook_url"])


if __name__ == "__main__":
    main()
