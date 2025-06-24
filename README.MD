# Proxmox Backup Checker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

Ein Python-Script zur automatischen Überwachung von Proxmox VE Backup-Jobs mit Benachrichtigungen an Home Assistant.

## 🚀 Quick Start

```bash
# Repository klonen
git clone https://github.com/yourusername/proxmox-backup-checker.git
cd proxmox-backup-checker

# Konfiguration erstellen
cp app/config.json.example app/config.json
# config.json mit deinen Daten anpassen

# Script ausführen
cd app && ./start.sh
```

## Funktionen

### Hauptfunktionen
- **Automatische Backup-Überwachung**: Prüft alle konfigurierten Backup-Jobs in Proxmox VE
- **Intelligente Zeitplan-Analyse**: Berücksichtigt individuelle Backup-Zeitpläne (täglich, wöchentlich, etc.)
- **Logfile-Analyse**: Analysiert Backup-Logfiles auf Erfolg oder Fehler
- **Home Assistant Integration**: Sendet Fehlermeldungen automatisch an Home Assistant
- **VM/CT-Namen-Auflösung**: Zeigt aussagekräftige Namen statt nur IDs

### Prüflogik
Das Script prüft für jede VM/CT:
1. **Zeitplan-Compliance**: Ist ein Backup laut Zeitplan fällig?
2. **Logfile-Existenz**: Existiert ein Logfile für die VM/CT?
3. **Aktualität**: Ist das Logfile nach dem letzten geplanten Backup-Termin erstellt worden?
4. **Fehlerfreiheit**: Enthält das Logfile Fehlermeldungen (ERROR, FAILED, aborted)?

### Debug-Modus
Umfassende Debug-Ausgaben zeigen:
- Alle gefundenen Backup-Jobs mit Zeitplänen
- VM/CT-IDs und Namen aus den Jobs
- Letzte geplante Ausführungstermine
- Erfolgreiche Backups mit Zeitstempel
- Fehlerhafte Backups mit Ursache
- Alle Logdateien im Verzeichnis

## Installation

### Voraussetzungen
- Python 3.6+
- Proxmox VE API-Token
- Home Assistant (optional)

### Setup
1. Repository klonen:
   ```bash
   git clone https://github.com/yourusername/proxmox-backup-checker.git
   cd proxmox-backup-checker
   ```

2. Konfiguration erstellen:
   ```bash
   cp app/config.json.example app/config.json
   ```

3. Konfiguration anpassen (siehe Konfiguration)

4. Script ausführen:
   ```bash
   cd app && ./start.sh
   ```

## Konfiguration

Bearbeite `app/config.json`:

```json
{
  "debug": true,
  "proxmox_host": "your-proxmox-host",
  "proxmox_api_token_user": "root@pam",
  "proxmox_api_token_name": "backupscript",
  "proxmox_api_token_secret": "your-api-token-secret",
  "proxmox_verify_ssl": false,
  "log_dir": "/var/log/vzdump",
  "ha_webhook_url": "http://your-homeassistant:8123/api/webhook/proxmox_backup_error"
}
```

### Konfigurationsparameter
- `debug`: Aktiviert ausführliche Debug-Ausgaben (true/false)
- `proxmox_host`: Hostname/IP des Proxmox-Servers
- `proxmox_api_token_*`: API-Token-Zugangsdaten
- `proxmox_verify_ssl`: SSL-Zertifikat prüfen (true/false)
- `log_dir`: Pfad zum Backup-Logverzeichnis
- `ha_webhook_url`: Home Assistant Webhook-URL für Benachrichtigungen

## Verwendung

### Manueller Start
```bash
cd app
python check_backups.py
```

### Mit Start-Script
```bash
cd app
./start.sh
```

### Automatisierung
Füge zu crontab hinzu für regelmäßige Prüfungen:
```bash
# Täglich um 6:00 Uhr prüfen
0 6 * * * /path/to/proxmox-backup-checker/app/start.sh
```

## Beispiel-Ausgabe

### Debug-Modus aktiviert
```
[DEBUG] Starte Analyse der Backup-Jobs...
[DEBUG] Job backup-daily: enabled=1, schedule='03:00' -> dow=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'], starttime='03:00', vmids=101,102,104
[DEBUG] Job backup-weekly: enabled=1, schedule='sun 01:00' -> dow=['sun'], starttime='01:00', vmids=103

[DEBUG] Gefundene VM/CT-IDs in Jobs: ['101', '102', '103', '104']
[DEBUG] VM/CT 101 - Letzter geplanter Termin: 2025-06-24 03:00:00
[DEBUG] VM/CT 103 - Letzter geplanter Termin: 2025-06-22 01:00:00

[DEBUG] Erfolgreiche Backups (nach Zeitplan):
  - VM/CT-ID: 101 (docker): Backup erfolgreich am 2025-06-24 03:01:58 (qemu-101.log)
  - VM/CT-ID: 102 (nextcloud): Backup erfolgreich am 2025-06-24 03:02:40 (qemu-102.log)
  - VM/CT-ID: 103 (webserver): Backup erfolgreich am 2025-06-22 01:03:40 (lxc-103.log)

[DEBUG] Fehlerhafte Backups:
  - VM/CT-ID: 104 (database): Logdatei nicht gefunden
```

## API-Token erstellen

1. Proxmox Web-Interface öffnen
2. Datacenter → Permissions → API Tokens
3. "Add" klicken
4. User: `root@pam`, Token ID: `backupscript`
5. Privilege Separation deaktivieren
6. Token-Secret kopieren und in config.json eintragen

## API-Verbindung testen

Vor dem ersten Einsatz kannst du die API-Verbindung testen:

```bash
cd app
python proxmox_token_test.py
```

**Erfolgreiche Ausgabe:**
```
Teste Verbindung zu your-proxmox-host mit Token root@pam@backupscript...
Erfolgreich verbunden! Proxmox Version: 8.2.2
```

**Bei Fehlern:**
- Prüfe Host-Erreichbarkeit
- Validiere API-Token-Daten in config.json
- Kontrolliere Netzwerk und SSL-Einstellungen

## Fehlerbehebung

### Häufige Probleme
- **Verbindungsfehler**: Proxmox-Host und API-Token prüfen
- **Keine Logfiles gefunden**: `log_dir` Pfad und Berechtigungen prüfen
- **Falsche Zeitpläne**: Debug-Modus aktivieren und Job-Parameter prüfen

### Debug-Modus nutzen
Setze `"debug": true` in der config.json für detaillierte Ausgaben.

## Home Assistant Integration

### Webhook einrichten
1. Home Assistant → Einstellungen → Automatisierungen & Szenen
2. Neue Automatisierung erstellen
3. Auslöser: Webhook mit ID `proxmox_backup_error`
4. Aktion: Benachrichtigung senden

### Beispiel-Automatisierung
```yaml
alias: Proxmox Backup Fehler
trigger:
  - platform: webhook
    webhook_id: proxmox_backup_error
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "Proxmox Backup Fehler"
      message: "{{ trigger.json.message }}"
```

## 🤝 Contributing

Beiträge sind willkommen! Bitte:

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne eine Pull Request

## 📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagung

- [proxmoxer](https://github.com/proxmoxer/proxmoxer) - Proxmox API Client
- Proxmox VE Team für die exzellente Virtualisierungsplattform 