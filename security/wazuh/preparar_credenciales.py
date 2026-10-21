"""Genera credenciales locales de Wazuh sin mostrarlas en consola.

Ejecutar una sola vez desde cualquier directorio. Requiere la imagen oficial
wazuh/wazuh-indexer:4.14.9 ya descargada.
"""

import os
from pathlib import Path
import re
import secrets
import string
import subprocess


ROOT = Path(__file__).resolve().parent / "upstream" / "single-node"
ENV_FILE = ROOT / ".env"
INDEXER_USERS = ROOT / "config" / "wazuh_indexer" / "internal_users.local.yml"
DASHBOARD_CONFIG = ROOT / "config" / "wazuh_dashboard" / "wazuh.local.yml"


def password():
    chars = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        "!",
    ]
    chars += [secrets.choice(string.ascii_letters + string.digits + "!_-.") for _ in range(24)]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def indexer_hash(cleartext):
    env = os.environ.copy()
    env["WAZUH_HASH_INPUT"] = cleartext
    command = [
        "docker", "run", "--rm", "-e", "WAZUH_HASH_INPUT",
        "-e", "JAVA_HOME=/usr/share/wazuh-indexer/jdk",
        "--entrypoint", "bash", "wazuh/wazuh-indexer:4.14.9",
        "/usr/share/wazuh-indexer/plugins/opensearch-security/tools/hash.sh",
        "-env", "WAZUH_HASH_INPUT",
    ]
    result = subprocess.run(command, env=env, capture_output=True, text=True, check=True)
    matches = re.findall(r"\$2[aby]\$\d\d\$[./A-Za-z0-9]{53}", result.stdout)
    if len(matches) != 1:
        raise RuntimeError("No se obtuvo exactamente un hash BCrypt oficial")
    return matches[0]


def main():
    if any(path.exists() for path in (ENV_FILE, INDEXER_USERS, DASHBOARD_CONFIG)):
        raise RuntimeError("Ya existe configuración local; se evita sobrescribir credenciales")

    admin, kibana, api = password(), password(), password()
    admin_hash, kibana_hash = indexer_hash(admin), indexer_hash(kibana)

    users = (
        '---\n_meta:\n  type: "internalusers"\n  config_version: 2\n'
        'admin:\n  hash: "' + admin_hash + '"\n  reserved: true\n'
        '  backend_roles:\n  - "admin"\n'
        'kibanaserver:\n  hash: "' + kibana_hash + '"\n  reserved: true\n'
    )
    dashboard = (ROOT / "config" / "wazuh_dashboard" / "wazuh.yml").read_text(encoding="utf-8")
    dashboard = dashboard.replace('password: "MyS3cr37P450r.*-"', f'password: "{api}"')
    if api not in dashboard:
        raise RuntimeError("No se encontró la contraseña de API original en wazuh.yml")

    env_text = (
        f"WAZUH_ADMIN_PASSWORD={admin}\n"
        f"WAZUH_KIBANA_PASSWORD={kibana}\n"
        f"WAZUH_API_PASSWORD={api}\n"
    )
    for path, content in ((ENV_FILE, env_text), (INDEXER_USERS, users), (DASHBOARD_CONFIG, dashboard)):
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
    print("Credenciales locales creadas. Archivo .env ignorado por Git; no mostrar su contenido en capturas.")


if __name__ == "__main__":
    main()
