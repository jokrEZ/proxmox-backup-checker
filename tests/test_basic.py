"""
Grundlegende Tests für den Proxmox Backup Checker
"""

import sys
import os
import pytest

# Füge das app-Verzeichnis zum Python-Path hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

def test_python_version():
    """Teste, ob Python-Version kompatibel ist"""
    assert sys.version_info >= (3, 8), "Python 3.8+ erforderlich"

def test_imports():
    """Teste, ob grundlegende Imports funktionieren"""
    try:
        import json
        import os
        import datetime
        import re
        assert True
    except ImportError as e:
        pytest.fail(f"Import-Fehler: {e}")

def test_app_structure():
    """Teste, ob die App-Struktur korrekt ist"""
    app_dir = os.path.join(os.path.dirname(__file__), '..', 'app')
    
    # Prüfe, ob wichtige Dateien existieren
    assert os.path.exists(os.path.join(app_dir, 'check_backups.py')), "check_backups.py nicht gefunden"
    assert os.path.exists(os.path.join(app_dir, 'config.json.example')), "config.json.example nicht gefunden"
    assert os.path.exists(os.path.join(app_dir, 'requirements.txt')), "requirements.txt nicht gefunden"

def test_config_example_structure():
    """Teste, ob die Beispiel-Konfiguration korrekt strukturiert ist"""
    import json
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'config.json.example')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Prüfe erforderliche Schlüssel
    required_keys = [
        'proxmox_host',
        'proxmox_api_token_user',
        'proxmox_api_token_name',
        'proxmox_api_token_secret',
        'proxmox_backup_dir',
        'home_assistant_webhook_url'
    ]
    
    for key in required_keys:
        assert key in config, f"Erforderlicher Schlüssel '{key}' fehlt in config.json.example"

def test_requirements_file():
    """Teste, ob requirements.txt korrekt formatiert ist"""
    req_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'requirements.txt')
    
    with open(req_path, 'r') as f:
        requirements = f.read().strip().split('\n')
    
    # Prüfe, ob proxmoxer enthalten ist
    proxmoxer_found = any('proxmoxer' in req for req in requirements)
    assert proxmoxer_found, "proxmoxer nicht in requirements.txt gefunden"
    
    # Prüfe, ob requests enthalten ist
    requests_found = any('requests' in req for req in requirements)
    assert requests_found, "requests nicht in requirements.txt gefunden"

class TestScheduleParser:
    """Tests für Schedule-Parsing-Logik (Mock-Tests)"""
    
    def test_daily_schedule_format(self):
        """Teste tägliche Schedule-Formate"""
        # Mock-Test ohne echte App-Imports
        daily_formats = ['03:00', '23:30', '12:15']
        
        for schedule in daily_formats:
            # Einfacher Regex-Test für Format
            import re
            pattern = r'^\d{2}:\d{2}$'
            assert re.match(pattern, schedule), f"Ungültiges tägliches Format: {schedule}"
    
    def test_weekly_schedule_format(self):
        """Teste wöchentliche Schedule-Formate"""
        weekly_formats = ['sun 01:00', 'mon 12:30', 'fri 23:45']
        
        for schedule in weekly_formats:
            import re
            pattern = r'^(sun|mon|tue|wed|thu|fri|sat) \d{2}:\d{2}$'
            assert re.match(pattern, schedule), f"Ungültiges wöchentliches Format: {schedule}"

if __name__ == '__main__':
    pytest.main([__file__]) 