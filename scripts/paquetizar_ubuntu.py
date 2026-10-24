"""Empaqueta únicamente el código y la configuración necesarios en Ubuntu."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist/uts-cwpp-ubuntu.zip"
FILES = [
    "README.md",
    "ubuntu.compose.yaml",
    "docs/arquitectura-ubuntu.svg",
    "docs/guia-reproduccion.md",
    "deploy/ubuntu/falco.compose.yaml",
    "deploy/ubuntu/wazuh-manager.compose.yaml",
    "deploy/ubuntu/wazuh-manager.Dockerfile",
    "deploy/ubuntu/wazuh-manager.conf",
    "deploy/ubuntu/wazuh-falco-rules.xml",
    "deploy/ubuntu/wazuh-portal-rules.xml",
    "app/backend/.dockerignore",
    "app/backend/Dockerfile",
    "app/backend/requirements.txt",
    "app/backend/app.py",
    "app/backend/templates/base.html",
    "app/backend/templates/index.html",
    "app/backend/templates/login.html",
    "app/backend/templates/tabla.html",
    "app/backend/static/style.css",
    "database/init/01_schema.sql",
    "scripts/preparar_ubuntu.py",
    "scripts/provision_demo_users.py",
    "scripts/smoke_portal.py",
    "scripts/verificar_falco_json.py",
    "scripts/verificar_wazuh_falco.py",
    "scripts/verificar_wazuh_portal_ubuntu.py",
]


def main():
    OUTPUT.parent.mkdir(exist_ok=True)
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as archive:
        for path in FILES:
            archive.write(ROOT / path, path)
    print(f"Paquete creado: {OUTPUT}")
    print(f"Archivos incluidos: {len(FILES)}")


if __name__ == "__main__":
    main()
