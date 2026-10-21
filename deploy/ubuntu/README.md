# Portal UTS en Ubuntu VirtualBox

Este paquete inicia el mismo portal de prueba y PostgreSQL **dentro de Ubuntu**. La imagen del portal se descarga de Docker Hub: `d4c5g/uts-cwpp-portal:2026-10-21` (`linux/amd64`). El archivo SQL incluido inicializa datos de demostración en un volumen nuevo; **no** copia los datos ni las contraseñas del Windows original.

## Arranque

1. Instala Ubuntu Server y Docker Engine con el complemento Compose en la VM. Usa la [guía oficial de Docker para Ubuntu](https://docs.docker.com/engine/install/ubuntu/). No uses Docker Desktop de Windows como motor de esta VM.
2. Copia y descomprime este ZIP en Ubuntu. Entra al directorio que contiene `compose.yaml`.
3. Ejecuta `python3 scripts/preparar_ubuntu.py`. Genera `.env` y `credenciales_portal.txt` **solo dentro de Ubuntu**. No publiques ni captures esos archivos.
4. Ejecuta `docker compose config --quiet`, `docker compose pull` y `docker compose up -d`.
5. Espera a que `docker compose ps -a` muestre `uts-database` y `uts-portal` como `healthy`. Comprueba `curl -fsS http://127.0.0.1:8080/health` dentro de Ubuntu y ejecuta `python3 scripts/smoke_portal.py`.

Para abrir el portal desde Windows con red NAT de VirtualBox: **Configuración de la VM → Red → Adaptador 1 → NAT → Avanzadas → Reenvío de puertos**. Añade TCP, IP anfitrión `127.0.0.1`, puerto anfitrión `18080`, puerto invitado `8080`. Después abre `http://localhost:18080` en Windows. La comprobación de `smoke_portal.py` se ejecuta dentro de Ubuntu y usa el puerto 8080 interno.

## Evidencia de Falco

Falco debe instalarse y ejecutarse **en esta misma VM**. Una vez que el portal esté saludable, provoca un evento de prueba controlado en `uts-portal` y verifica que la salida de Falco mencione ese contenedor. Captura `docker compose ps -a` y la alerta real con nombre de regla, hora y contenedor. Un Falco instalado en otra VM o en Windows no demuestra cobertura de este portal.

Conserva los volúmenes: para detener usa `docker compose stop`; no uses `docker compose down -v`. La imagen del portal conserva el hallazgo alto de `zlib` documentado en el escaneo previo; subirla a Docker Hub no corrige esa vulnerabilidad.
