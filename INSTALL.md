# 🚀 Server-Installation - Proxmox Backup Checker

## Voraussetzungen

- **Python 3.8+** auf dem Server
- **Git** installiert
- **Zugriff** auf Proxmox VE API
- **Home Assistant** mit Webhook-URL

## 📦 Installation

### Option 1: Direkt von GitHub (Empfohlen)

```bash
# 1. Repository klonen
git clone https://github.com/jokrEZ/proxmox-backup-checker.git
cd proxmox-backup-checker

# 2. Python Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# 3. Paket installieren
pip install .

# 4. Konfiguration erstellen
cp app/config.json.example app/config.json
nano app/config.json  # oder vi/vim
```

### Option 2: Als Python Package

```bash
# Direkt installieren (ohne Repository klonen)
pip install git+https://github.com/jokrEZ/proxmox-backup-checker.git

# Konfigurationsdatei erstellen
mkdir -p /opt/proxmox-backup-checker
cd /opt/proxmox-backup-checker
wget https://raw.githubusercontent.com/jokrEZ/proxmox-backup-checker/main/app/config.json.example -O config.json
nano config.json
```

## ⚙️ Konfiguration

### config.json bearbeiten:

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

### Proxmox API-Token erstellen:

1. **Proxmox Web UI** → Datacenter → Permissions → API Tokens
2. **Add** → User: `root@pam`, Token ID: `backup-checker`
3. **Privilege Separation** deaktivieren (oder entsprechende Rechte vergeben)
4. **Token Secret** kopieren und in config.json eintragen

## 🔄 Ausführung

### Manuell testen:

```bash
# Mit installiertem Package
proxmox-backup-checker

# Oder direkt im Repository
cd /path/to/proxmox-backup-checker
python app/check_backups.py

# Mit Debug-Modus
CONFIG_PATH=/path/to/config.json proxmox-backup-checker
```

### Automatisierung mit Cron:

```bash
# Crontab bearbeiten
crontab -e

# Beispiel: Jeden Tag um 8:00 Uhr prüfen
0 8 * * * /opt/proxmox-backup-checker/venv/bin/proxmox-backup-checker

# Oder mit expliziter Konfiguration
0 8 * * * CONFIG_PATH=/opt/proxmox-backup-checker/config.json /usr/local/bin/proxmox-backup-checker

# Mit Logging
0 8 * * * /usr/local/bin/proxmox-backup-checker >> /var/log/backup-checker.log 2>&1
```

### Systemd Service (Empfohlen):

```bash
# Service-Datei erstellen
sudo nano /etc/systemd/system/proxmox-backup-checker.service
```

**Service-Inhalt:**
```ini
[Unit]
Description=Proxmox Backup Checker
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/proxmox-backup-checker
Environment=CONFIG_PATH=/opt/proxmox-backup-checker/config.json
ExecStart=/usr/local/bin/proxmox-backup-checker
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Timer erstellen:**
```bash
sudo nano /etc/systemd/system/proxmox-backup-checker.timer
```

**Timer-Inhalt:**
```ini
[Unit]
Description=Run Proxmox Backup Checker daily
Requires=proxmox-backup-checker.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

**Aktivieren:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable proxmox-backup-checker.timer
sudo systemctl start proxmox-backup-checker.timer

# Status prüfen
sudo systemctl status proxmox-backup-checker.timer
sudo systemctl list-timers proxmox-backup-checker*
```

## 🔍 Troubleshooting

### Debug-Modus aktivieren:

```bash
# In config.json
"debug": true

# Oder als Umgebungsvariable
DEBUG=true proxmox-backup-checker
```

### Logs prüfen:

```bash
# Systemd Logs
sudo journalctl -u proxmox-backup-checker.service -f

# Eigene Log-Datei
tail -f /var/log/backup-checker.log
```

### Häufige Probleme:

1. **SSL-Fehler**: `"proxmox_verify_ssl": false` in config.json
2. **API-Token**: Rechte in Proxmox prüfen
3. **Pfade**: Backup-Verzeichnis korrekt angeben
4. **Netzwerk**: Firewall/Routing zu Proxmox und Home Assistant

## 📁 Empfohlene Verzeichnisstruktur:

```
/opt/proxmox-backup-checker/
├── venv/                    # Python Virtual Environment
├── config.json             # Konfiguration
├── backup-checker.log      # Log-Datei (optional)
└── README.md               # Diese Anleitung
```

## 🔄 Updates:

```bash
# Repository-Installation
cd /opt/proxmox-backup-checker
git pull origin main
pip install . --upgrade

# Package-Installation
pip install --upgrade git+https://github.com/jokrEZ/proxmox-backup-checker.git
``` 