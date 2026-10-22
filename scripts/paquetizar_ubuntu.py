"""Empaqueta solo los archivos necesarios para la VM; lista blanca explícita."""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist/uts-cwpp-ubuntu-2026-10-21.zip"
FILES = [
    ("deploy/ubuntu/compose.yaml", "compose.yaml"),
    ("deploy/ubuntu/falco.compose.yaml", "falco.compose.yaml"),
    ("deploy/ubuntu/falco.compose.yaml", "deploy/ubuntu/falco.compose.yaml"),
    ("deploy/ubuntu/wazuh-manager.compose.yaml", "deploy/ubuntu/wazuh-manager.compose.yaml"),
    ("deploy/ubuntu/wazuh-manager.Dockerfile", "deploy/ubuntu/wazuh-manager.Dockerfile"),
    ("deploy/ubuntu/wazuh-manager.conf", "deploy/ubuntu/wazuh-manager.conf"),
    ("deploy/ubuntu/wazuh-falco-rules.xml", "deploy/ubuntu/wazuh-falco-rules.xml"),
    ("deploy/ubuntu/wazuh-portal-rules.xml", "deploy/ubuntu/wazuh-portal-rules.xml"),
    ("deploy/ubuntu/README.md", "README.md"),
    ("database/init/01_schema.sql", "database/init/01_schema.sql"),
    ("scripts/preparar_ubuntu.py", "scripts/preparar_ubuntu.py"),
    ("scripts/provision_demo_users.py", "scripts/provision_demo_users.py"),
    ("scripts/smoke_portal.py", "scripts/smoke_portal.py"),
    ("scripts/verificar_falco_json.py", "scripts/verificar_falco_json.py"),
    ("scripts/verificar_wazuh_falco.py", "scripts/verificar_wazuh_falco.py"),
    ("scripts/verificar_wazuh_portal_ubuntu.py", "scripts/verificar_wazuh_portal_ubuntu.py"),
    ("docs/fase-f-falco-ubuntu.md", "docs/fase-f-falco-ubuntu.md"),
    ("docs/fase-h-preparacion-wazuh-falco.md", "docs/fase-h-preparacion-wazuh-falco.md"),
    ("docs/fase-i-auditoria-wazuh-ubuntu.md", "docs/fase-i-auditoria-wazuh-ubuntu.md"),
    ("docs/evidencias/wazuh-falco-ubuntu-verificacion.json", "docs/evidencias/wazuh-falco-ubuntu-verificacion.json"),
    ("docs/evidencias/wazuh-portal-ubuntu-verificacion.json", "docs/evidencias/wazuh-portal-ubuntu-verificacion.json"),
]


def main():
    OUTPUT.parent.mkdir(exist_ok=True)
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as archive:
        for source, destination in FILES:
            if source == "deploy/ubuntu/README.md":
                # En el ZIP este README vive en la raíz, junto a docs/.
                content = (ROOT / source).read_text(encoding="utf-8")
                archive.writestr(destination, content.replace("../../docs/", "docs/"))
            else:
                archive.write(ROOT / source, destination)
    print(f"Paquete creado: {OUTPUT}")
    print("Archivos incluidos:")
    for _, destination in FILES:
        print(f"  {destination}")


if __name__ == "__main__":
    main()
