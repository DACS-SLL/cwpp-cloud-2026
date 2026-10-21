"""Provisiona cuentas de demostración sin alterar la contraseña de PostgreSQL."""

import base64
import hashlib
import json
import os
from pathlib import Path
import secrets


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
CREDENTIALS_PATH = ROOT / "credenciales_portal.txt"


def main():
    existing = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.exists() else ""
    if "PORTAL_SECRET_KEY=" in existing or "PORTAL_USERS_B64=" in existing:
        raise SystemExit("La configuración del portal ya existe. No se han rotado credenciales.")
    if CREDENTIALS_PATH.exists():
        raise SystemExit("Ya existe un archivo de credenciales; revisa su estado antes de continuar.")

    accounts = {
        "estudiante_demo": {"role": "estudiante", "student_id": 1},
        "docente_demo": {"role": "docente"},
        "admin_demo": {"role": "administrador"},
    }
    passwords = {}
    for username, account in accounts.items():
        password = secrets.token_urlsafe(18)
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600000)
        account.update(salt=salt.hex(), hash=digest.hex())
        passwords[username] = password

    users_b64 = base64.b64encode(json.dumps(accounts, separators=(",", ":")).encode("utf-8")).decode("ascii")
    secret_key = secrets.token_hex(32)
    separator = "" if not existing or existing.endswith("\n") else "\n"
    ENV_PATH.write_text(existing + separator + f"PORTAL_SECRET_KEY={secret_key}\nPORTAL_USERS_B64={users_b64}\n", encoding="utf-8")
    fd = os.open(CREDENTIALS_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        output.write("Cuentas locales de prueba. Borra este archivo después de guardar las contraseñas.\n")
        for username, password in passwords.items():
            output.write(f"{username}={password}\n")
    print("Cuentas de prueba creadas. Consulta credenciales_portal.txt localmente; no lo publiques.")


if __name__ == "__main__":
    main()
