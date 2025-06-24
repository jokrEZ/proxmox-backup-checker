#!/bin/bash

# Proxmox Backup Checker - Start Script
# Automatisiertes Setup und Ausführung des Backup-Prüfskripts

set -e  # Bei Fehlern abbrechen

echo "=== Proxmox Backup Checker ==="
echo "Starte Backup-Überwachung..."

# Wechsle ins Verzeichnis, in dem das Script liegt
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Arbeitsverzeichnis: $SCRIPT_DIR"

# Prüfe, ob Python 3 verfügbar ist
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python 3 ist nicht installiert oder nicht im PATH verfügbar."
    exit 1
fi

# Virtuelle Umgebung anlegen, falls nicht vorhanden
if [ ! -d "venv" ]; then
    echo "Erstelle virtuelle Python-Umgebung..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "FEHLER: Konnte virtuelle Umgebung nicht erstellen."
        exit 1
    fi
fi

# Virtuelle Umgebung aktivieren
echo "Aktiviere virtuelle Umgebung..."
source venv/bin/activate

# Prüfe, ob requirements.txt existiert
if [ ! -f "requirements.txt" ]; then
    echo "FEHLER: requirements.txt nicht gefunden."
    exit 1
fi

# Abhängigkeiten installieren/aktualisieren
echo "Installiere/aktualisiere Abhängigkeiten..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Prüfe, ob config.json existiert
if [ ! -f "config.json" ]; then
    echo "WARNUNG: config.json nicht gefunden."
    echo "Erstelle Beispiel-Konfiguration..."
    cat > config.json << EOF
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
EOF
    echo "Bitte config.json mit deinen Zugangsdaten anpassen und das Script erneut ausführen."
    exit 1
fi

# Prüfe, ob check_backups.py existiert
if [ ! -f "check_backups.py" ]; then
    echo "FEHLER: check_backups.py nicht gefunden."
    exit 1
fi

# Script ausführen
echo "Starte Backup-Prüfung..."
echo "=========================="
python3 check_backups.py

# Exit-Code weiterleiten
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "=========================="
    echo "Backup-Prüfung erfolgreich abgeschlossen."
else
    echo "=========================="
    echo "FEHLER: Backup-Prüfung fehlgeschlagen (Exit-Code: $EXIT_CODE)"
fi

exit $EXIT_CODE 