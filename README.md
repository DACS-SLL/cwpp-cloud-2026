# Prototipo CWPP UTS

Portal académico de demostración con Flask, PostgreSQL, Falco y Wazuh manager en una VM Ubuntu. Todos los datos académicos y usuarios son ficticios. El despliegue de Wazuh incluye solo el manager: no incluye indexer ni dashboard.

![Arquitectura del prototipo](docs/arquitectura-ubuntu.svg)

## Contenido

- `app/backend/`: aplicación, interfaz y Dockerfile del portal.
- `database/init/`: esquema y datos de demostración.
- `ubuntu.compose.yaml`: portal, PostgreSQL, redes y volúmenes.
- `deploy/ubuntu/`: configuración Compose de Falco y Wazuh, reglas y Dockerfile del manager.
- `scripts/`: preparación local, empaquetado y verificadores funcionales.
- `docs/guia-reproduccion.md`: instalación y validación paso a paso.

## Inicio rápido en Ubuntu

Requiere Docker Engine con el complemento Compose, Python 3, Git y acceso a Internet en la primera construcción. Revisa memoria y disco con `free -h` y `df -h /` antes de arrancar Wazuh.

```bash
git clone https://github.com/DACS-SLL/cwpp-cloud-2026.git
cd cwpp-cloud-2026
python3 scripts/preparar_ubuntu.py
sudo docker compose -f ubuntu.compose.yaml up -d --build
sudo docker compose -f ubuntu.compose.yaml ps -a
curl -fsS http://127.0.0.1:8080/health
python3 scripts/smoke_portal.py
```

La preparación genera `.env` y `credenciales_portal.txt` solo en el equipo local. Ambos quedan fuera de Git. Para activar Falco, conectar las dos fuentes con Wazuh y comprobar las reglas 100100, 100101 y 100200, sigue la [guía de reproducción](docs/guia-reproduccion.md).

El portal escucha en el puerto 8080 de la VM. Con VirtualBox NAT, un reenvío local `127.0.0.1:18080` → `8080` permite abrirlo desde Windows en `http://localhost:18080`.

## Archivos generados

Los datos de PostgreSQL y los registros de auditoría de Wazuh viven en volúmenes Docker. Falco escribe en `falco-logs/`. Estos registros, las credenciales, capturas y paquetes `dist/` no forman parte del repositorio. Para detener los servicios sin borrar los volúmenes:

```bash
sudo docker compose -f ubuntu.compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml stop
```

`python3 scripts/paquetizar_ubuntu.py` crea un ZIP de código y configuración en `dist/`, sin credenciales, logs ni evidencias.
