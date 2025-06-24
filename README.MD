# 🔍 Proxmox Backup Checker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Quality & Security](https://github.com/jokrEZ/proxmox-backup-checker/actions/workflows/python-app.yml/badge.svg)](https://github.com/jokrEZ/proxmox-backup-checker/actions/workflows/python-app.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**Intelligente Überwachung von Proxmox VE Backup-Jobs mit Home Assistant Integration**

Automatische Prüfung deiner Proxmox-Backups basierend auf den konfigurierten Zeitplänen - nur echte Probleme werden gemeldet, keine false positives!

## ✨ Features

- 🕐 **Zeitplan-bewusste Prüfung** - Respektiert individuelle Backup-Schedules (täglich/wöchentlich)
- 🔍 **Intelligente Log-Analyse** - Erkennt echte Backup-Fehler in Logdateien
- 🏠 **Home Assistant Integration** - Webhook-Benachrichtigungen bei Problemen
- 📝 **VM/CT-Namen-Auflösung** - Zeigt aussagekräftige Namen statt nur IDs
- 🐛 **Umfassender Debug-Modus** - Detaillierte Informationen für Troubleshooting
- ⚡ **Einfache Installation** - Als Python Package oder Git Repository

## 🚀 Quick Start

```bash
# Einfachste Installation
pip install git+https://github.com/jokrEZ/proxmox-backup-checker.git

# Konfiguration erstellen
wget https://raw.githubusercontent.com/jokrEZ/proxmox-backup-checker/main/app/config.json.example -O config.json
nano config.json  # Deine Proxmox & Home Assistant Daten eintragen

# Ausführen
proxmox-backup-checker
```

📋 **[Detaillierte Installationsanleitung →](INSTALL.md)**

## 🧠 Wie es funktioniert

### Intelligente Prüflogik
Das Tool analysiert für jede VM/CT:

1. **📅 Zeitplan-Compliance** - Ist laut Schedule ein Backup fällig?
2. **📄 Logfile-Existenz** - Gibt es ein aktuelles Logfile?
3. **⏰ Aktualität** - Wurde das Backup nach dem geplanten Termin erstellt?
4. **✅ Fehlerfreiheit** - Enthält das Log Fehlermeldungen (ERROR, FAILED, aborted)?

**Nur wenn alle Kriterien fehlschlagen, wird eine Benachrichtigung gesendet!**

### Unterstützte Backup-Zeitpläne
- **Täglich**: `03:00` (jeden Tag um 3:00 Uhr)
- **Wöchentlich**: `sun 01:00` (Sonntags um 1:00 Uhr)
- **Komplex**: Beliebige Kombinationen möglich

## ⚙️ Konfiguration

Erstelle eine `config.json` mit deinen Daten:

```json
{
    "proxmox_host": "192.168.1.100:8006",
    "proxmox_api_token_user": "root@pam!backup-checker",
    "proxmox_api_token_name": "backup-checker",
    "proxmox_api_token_secret": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "proxmox_verify_ssl": false,
    "proxmox_backup_dir": "/var/log/vzdump",
    "home_assistant_webhook_url": "https://your-ha.duckdns.org/api/webhook/backup-alerts",
    "debug": false
}
```

### 🔑 Proxmox API-Token erstellen
1. **Proxmox Web UI** → Datacenter → Permissions → API Tokens
2. **Add** → User: `root@pam`, Token ID: `backup-checker`
3. **Privilege Separation** deaktivieren
4. **Token Secret** kopieren und in config.json eintragen

## 🏠 Home Assistant Integration

### Webhook einrichten
```yaml
# configuration.yaml
automation:
  - alias: "Proxmox Backup Fehler"
    trigger:
      - platform: webhook
        webhook_id: backup-alerts
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🚨 Proxmox Backup Fehler"
          message: "{{ trigger.json.message }}"
```

### Webhook-URL
`https://your-ha.duckdns.org/api/webhook/backup-alerts`

## 📊 Beispiel-Ausgabe

### Debug-Modus
```bash
# Debug aktivieren
proxmox-backup-checker  # mit "debug": true in config.json
```

```
[DEBUG] Erfolgreiche Backups (nach Zeitplan):
  - VM/CT-ID: 101 (docker): Backup erfolgreich am 2025-06-24 03:01:58
  - VM/CT-ID: 102 (nextcloud): Backup erfolgreich am 2025-06-24 03:02:40

[DEBUG] Fehlerhafte Backups:
  - VM/CT-ID: 104 (database): Logdatei nicht gefunden
```

### Home Assistant Benachrichtigung
```
🚨 Proxmox Backup Fehler
Backup-Fehler bei database (ID: 104): Logdatei nicht gefunden
```

## 🔧 Entwicklung & Beiträge

```bash
# Repository für Entwicklung klonen
git clone https://github.com/jokrEZ/proxmox-backup-checker.git
cd proxmox-backup-checker

# Development-Installation
pip install -e .[dev]

# Code-Qualität prüfen
black app/
isort app/
flake8 app/
```

**Beiträge sind willkommen!** 🎉 Bitte erstelle einen Pull Request oder öffne ein Issue.

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.

---

**⭐ Hat dir das Tool geholfen? Gib dem Repository einen Stern!** 