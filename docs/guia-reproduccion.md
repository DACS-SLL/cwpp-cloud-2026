# Reproducir el piloto CWPP UTS en Ubuntu

## Alcance y requisitos previos

Esta guía usa una VM **Ubuntu Linux x86-64** con Docker Engine, complemento Compose, Python 3 y Git. Necesita acceso a Internet para obtener `postgres:17-alpine`, `falcosecurity/falco:0.45.0`, `wazuh/wazuh-manager:4.14.9` y las dependencias de Python del portal durante la primera construcción. La instalación de Docker se explica en la [guía oficial para Ubuntu](https://docs.docker.com/engine/install/ubuntu/). La prueba original se hizo en VirtualBox con 3,8 GiB de RAM y 29 GB de disco; **no es un dimensionamiento recomendado**. Antes de construir Wazuh comprueba `free -h` y `df -h /` y deja varios GiB libres.

El piloto no incluye Wazuh indexer ni dashboard en Ubuntu. El portal y la base usan datos ficticios. Ejecuta los comandos desde la raíz del clon. Si tu usuario aún no pertenece al grupo Docker, conserva `sudo` como se muestra. No pegues el contenido de archivos de credenciales en una conversación o captura.

## 1. Obtener código y preparar secretos locales

```bash
git clone https://github.com/DACS-SLL/cwpp-cloud-2026.git
cd cwpp-cloud-2026
git log -1 --oneline
python3 scripts/preparar_ubuntu.py
sudo docker compose -f ubuntu.compose.yaml config --quiet
```

`preparar_ubuntu.py` crea `.env` y `credenciales_portal.txt` con permisos restringidos y se niega a sobrescribirlos. Estos archivos están excluidos de Git. En un clon usado, conserva sus valores existentes; para actualizar código usa `git pull --ff-only` solo después de revisar cambios locales.

Si recibiste el ZIP del prototipo, descomprímelo en Ubuntu y entra en esa carpeta. Los siguientes comandos usan las mismas rutas del clon; omite `git clone` y `git pull`.

## 2. Construir el portal y levantar PostgreSQL

```bash
sudo docker compose -f ubuntu.compose.yaml pull database
sudo docker compose -f ubuntu.compose.yaml up -d --build
sudo docker compose -f ubuntu.compose.yaml ps -a
curl -fsS http://127.0.0.1:8080/health
python3 scripts/smoke_portal.py
```

Espera los estados `healthy` de `uts-database` y `uts-portal`. El verificador utiliza las cuentas locales y confirma los tres roles, recuentos de demostración, denegación de acceso y salida. El portal se construye desde `app/backend` y se etiqueta `uts-cwpp-portal:local`. Tanto el clon como el ZIP usan `ubuntu.compose.yaml`.

Para acceder desde Windows con VirtualBox NAT, añade reenvío TCP anfitrión `127.0.0.1:18080` → invitado `8080`; luego abre `http://localhost:18080`. El puerto 2222 → 22 se usó para SSH. Configura los reenvíos desde VirtualBox; no abras el portal a una red pública.

## 3. Activar Falco y validar un evento nuevo

```bash
sudo install -d -m 0700 falco-logs
sudo docker compose -f ubuntu.compose.yaml -f deploy/ubuntu/falco.compose.yaml config --quiet
sudo docker compose -f ubuntu.compose.yaml -f deploy/ubuntu/falco.compose.yaml up -d falco
sudo docker exec -it uts-portal sh -c 'echo prueba-falco-json'
sudo python3 scripts/verificar_falco_json.py
```

Falco usa el kernel de la **misma VM**. El script confirma una línea JSON con regla, contenedor y marcador en `falco-logs/events.jsonl`; todavía no demuestra una alerta Wazuh. La detección sobre Docker Desktop de Windows no forma parte de esta prueba.

## 4. Activar Wazuh manager y ambas fuentes

El manager lee `falco-logs/events.jsonl` y el volumen `audit_logs` en solo lectura. El grupo numérico 999 es el grupo Wazuh en la imagen utilizada. Primero prepara los permisos después de que el portal haya escrito al menos un evento:

```bash
sudo chgrp 999 falco-logs falco-logs/events.jsonl
sudo chmod 2750 falco-logs
sudo chmod 640 falco-logs/events.jsonl
sudo docker volume inspect uts-cwpp-ubuntu_audit_logs >/dev/null
sudo docker run --rm --network none --entrypoint sh -v uts-cwpp-ubuntu_audit_logs:/var/log/uts postgres:17-alpine -c 'chgrp 999 /var/log/uts /var/log/uts/audit.jsonl* && chmod 2750 /var/log/uts && chmod 640 /var/log/uts/audit.jsonl*'
```

El portal tiene todas sus capacidades eliminadas; incluso `docker exec -u 0` no pudo cambiar el grupo del volumen. El contenedor auxiliar temporal modifica únicamente ese volumen, no usa red y desaparece al terminar.

```bash
sudo docker compose -f ubuntu.compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml config --quiet
sudo docker compose -f ubuntu.compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml up -d --build wazuh_manager
sleep 60
sudo docker ps --filter name=uts- --format 'table {{.Names}}\t{{.Status}}'
sudo docker exec uts-wazuh-manager /var/ossec/bin/wazuh-control status
```

Comprueba sobre todo `wazuh-analysisd` y `wazuh-logcollector`. Algunos servicios opcionales figuran detenidos y `wazuh-control status` puede devolver código distinto de cero. Si no arrancan los procesos necesarios, consulta `sudo docker logs --tail=80 uts-wazuh-manager`.

## 5. Verificar alertas reales y salud

```bash
sudo docker exec -it uts-portal sh -c 'echo prueba-falco-wazuh'
sudo python3 scripts/verificar_wazuh_falco.py
sudo python3 scripts/verificar_wazuh_portal_ubuntu.py
curl -fsS http://127.0.0.1:8080/health
```

El primer verificador debe localizar en `alerts.json` la regla **100200** originada por Falco. El segundo genera accesos de prueba y debe localizar alertas **100100** (`login_failed`) y **100101** (`access_denied`) posteriores a su inicio. Los códigos 100102/100103 están configurados, pero necesitan una prueba de caída aparte para reclamar una alerta en vivo. `data_access` es auditoría del portal, no auditoría interna de PostgreSQL.

## 6. Actualizar y detener

Para actualizar el front desde un commit nuevo sin reconstruir los otros servicios:

```bash
git pull --ff-only
sudo docker compose -f ubuntu.compose.yaml up -d --build --no-deps portal
sudo docker compose -f ubuntu.compose.yaml ps -a
curl -fsS http://127.0.0.1:8080/health
sudo python3 scripts/smoke_portal.py
```

La recreación del portal puede generar nuevos eventos Falco. Para detener sin borrar datos usa `sudo docker compose -f ubuntu.compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml stop`. `down -v` elimina los volúmenes persistentes. Revisa periódicamente el tamaño de `falco-logs/events.jsonl` con `sudo du -h`; ese archivo no rota automáticamente.
