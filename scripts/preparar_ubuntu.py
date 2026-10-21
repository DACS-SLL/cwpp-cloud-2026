"""Crea credenciales locales para el paquete Ubuntu sin imprimir secretos."""

import os
from pathlib import Path
import secrets
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"
CREDENTIALS = ROOT / "credenciales_portal.txt"


def main():
    if ENV.exists() or CREDENTIALS.exists():
        raise SystemExit("Ya existen credenciales locales. No se sobrescribieron.")
    previous_umask = os.umask(0o077)
    try:
        ENV.write_text(f"DB_PASSWORD={secrets.token_urlsafe(24)}\n", encoding="utf-8")
        os.chmod(ENV, 0o600)
        subprocess.run([sys.executable, str(ROOT / "scripts/provision_demo_users.py")], check=True)
    finally:
        os.umask(previous_umask)
    print("Archivo .env creado localmente. No lo subas a Docker Hub ni lo incluyas en capturas.")


if __name__ == "__main__":
    main()
