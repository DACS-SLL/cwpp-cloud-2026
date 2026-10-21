"""Empaqueta solo los archivos necesarios para la VM; lista blanca explícita."""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist/uts-cwpp-ubuntu-2026-10-21.zip"
FILES = {
    "deploy/ubuntu/compose.yaml": "compose.yaml",
    "deploy/ubuntu/README.md": "README.md",
    "database/init/01_schema.sql": "database/init/01_schema.sql",
    "scripts/preparar_ubuntu.py": "scripts/preparar_ubuntu.py",
    "scripts/provision_demo_users.py": "scripts/provision_demo_users.py",
    "scripts/smoke_portal.py": "scripts/smoke_portal.py",
}


def main():
    OUTPUT.parent.mkdir(exist_ok=True)
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as archive:
        for source, destination in FILES.items():
            archive.write(ROOT / source, destination)
    print(f"Paquete creado: {OUTPUT}")
    print("Archivos incluidos:")
    for destination in FILES.values():
        print(f"  {destination}")


if __name__ == "__main__":
    main()
