import os
import json
from proxmoxer import ProxmoxAPI

CONFIG_PATH = os.getenv("CONFIG_PATH", "config.json")


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der Konfiguration: {e}")
        exit(1)


def test_proxmox_token():
    config = load_config()
    user = config.get("proxmox_api_token_user")
    token_name = config.get("proxmox_api_token_name")
    token_secret = config.get("proxmox_api_token_secret")
    host = config.get("proxmox_host")
    verify_ssl = config.get("proxmox_verify_ssl", False)

    if not user or not token_name or not token_secret:
        print("Fehler: Kein API-Token in der config.json gefunden!")
        exit(1)

    print(f"Teste Verbindung zu {host} mit Token {user}@{token_name}...")
    try:
        proxmox = ProxmoxAPI(
            host,
            user=user,
            token_name=token_name,
            token_value=token_secret,
            verify_ssl=verify_ssl,
            backend="https",
        )
        # Test: Hole die Version der API
        version = proxmox.version.get()
        print(f"Erfolgreich verbunden! Proxmox Version: {version['version']}")
    except Exception as e:
        print(f"Fehler bei der Authentifizierung: {e}")
        import traceback

        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    test_proxmox_token()
