# Portal UTS en Ubuntu VirtualBox

Este paquete inicia el mismo portal de prueba y PostgreSQL **dentro de Ubuntu**. El portal se construye desde `app/backend` del repositorio o ZIP y se etiqueta `uts-cwpp-portal:local`; así la interfaz y el código corresponden al commit usado. La imagen anterior `d4c5g/uts-cwpp-portal:2026-10-21` queda como referencia histórica de las pruebas previas. El archivo SQL incluido inicializa datos de demostración en un volumen nuevo; **no** copia los datos ni las contraseñas del Windows original.

Esta guía describe principalmente el **ZIP**, donde el archivo base se llama `compose.yaml`. En un **clon Git nuevo** usa el archivo versionado `ubuntu.compose.yaml` en su lugar y sigue [la guía completa de reproducción](../../docs/guia-reproduccion.md). En un clon antiguo puede existir un `compose.yaml` local extraído del ZIP; el archivo `ubuntu.compose.yaml` actualizado evita sobrescribirlo y es el que debe usarse para el front nuevo.

## Arranque

1. Instala Ubuntu Server y Docker Engine con el complemento Compose en la VM. Usa la [guía oficial de Docker para Ubuntu](https://docs.docker.com/engine/install/ubuntu/). No uses Docker Desktop de Windows como motor de esta VM.
2. Copia y descomprime este ZIP en Ubuntu. Entra al directorio que contiene `compose.yaml`.
3. Ejecuta `python3 scripts/preparar_ubuntu.py`. Genera `.env` y `credenciales_portal.txt` **solo dentro de Ubuntu**. No publiques ni captures esos archivos.
4. Ejecuta `docker compose config --quiet`, `docker compose pull database` y `docker compose up -d --build`.
5. Espera a que `docker compose ps -a` muestre `uts-database` y `uts-portal` como `healthy`. Comprueba `curl -fsS http://127.0.0.1:8080/health` dentro de Ubuntu y ejecuta `python3 scripts/smoke_portal.py`.

Para abrir el portal desde Windows con red NAT de VirtualBox: **Configuración de la VM → Red → Adaptador 1 → NAT → Avanzadas → Reenvío de puertos**. Añade TCP, IP anfitrión `127.0.0.1`, puerto anfitrión `18080`, puerto invitado `8080`. Después abre `http://localhost:18080` en Windows. La comprobación de `smoke_portal.py` se ejecuta dentro de Ubuntu y usa el puerto 8080 interno.

Para actualizar **solo la interfaz** de una instalación existente en el clon Git, primero guarda cualquier cambio local, ejecuta `git pull --ff-only` y luego `sudo docker compose -f ubuntu.compose.yaml up -d --build --no-deps portal`. En el ZIP usa `-f compose.yaml`. Espera a que `uts-portal` esté `healthy` y ejecuta `sudo python3 scripts/smoke_portal.py` y `curl -fsS http://127.0.0.1:8080/health`. Este comando reconstruye y recrea el contenedor del portal; los volúmenes `postgres_data` y `audit_logs` permanecen. Falco observará ese reinicio y la nueva etiqueta de imagen en eventos posteriores. Las capturas previas corresponden al despliegue anterior y no se deben presentar como prueba visual de esta interfaz.

## Evidencia de Falco

Falco 0.45.0 se ejecutó **en esta misma VM** y observó dos aperturas de shell en `uts-portal`, incluida la prueba `sh -c echo prueba-falco`. El log atribuyó ambas al contenedor y a la imagen del portal. Para volver a consultar las alertas:

```bash
sudo docker logs --tail=100 uts-falco 2>&1 | grep -F 'container_name=uts-portal'
```

Captura `sudo docker compose -f compose.yaml ps -a` y las líneas de alerta con hora y contenedor. Si en el directorio existen tanto `compose.yaml` como `compose.yml`, indica `-f compose.yaml` para evitar que Compose elija uno implícitamente. La prueba y su alcance están en [docs/fase-f-falco-ubuntu.md](../../docs/fase-f-falco-ubuntu.md). Falco en esta VM observa el portal de la VM; no se ha demostrado cobertura del portal en Docker Desktop de Windows.

### Arranque reproducible de Falco

El archivo `falco.compose.yaml` reproduce el despliegue que generó las alertas. Desde el directorio del proyecto en Ubuntu:

```bash
sudo docker compose -f compose.yaml -f falco.compose.yaml config --quiet
sudo docker compose -f compose.yaml -f falco.compose.yaml up -d falco
sudo docker compose -f compose.yaml -f falco.compose.yaml ps -a
```

Si actualizas una copia clonada con `git pull` y conservas `compose.yaml` en la raíz, usa `-f compose.yaml -f deploy/ubuntu/falco.compose.yaml` en los tres comandos. El ZIP actualizado coloca ambos archivos en la raíz.

Si `uts-falco` ya existe porque se inició manualmente, **antes** de usar Compose guarda su salida y retira solo ese contenedor:

```bash
sudo docker logs uts-falco > ~/falco-previo.log 2>&1
sudo docker stop uts-falco
```

Si `docker stop` deja el contenedor creado, ejecuta `sudo docker rm uts-falco`. Si el contenedor manual se inició con `--rm`, Docker lo elimina automáticamente al detenerlo y el comando `rm` no hace falta. Después ejecuta el `up -d falco` indicado arriba. `~/falco-previo.log` puede incluir comandos y rutas del sistema: consérvalo fuera del repositorio y revísalo antes de compartirlo. El cambio no toca el portal, PostgreSQL ni sus volúmenes. Falco necesita privilegios elevados y montajes del host para observar el kernel; no atribuyas al sensor las restricciones de seguridad del contenedor del portal. Los montajes y la versión de la imagen siguen la [guía oficial de Falco para contenedores](https://falco.org/docs/setup/container/).

Tras levantar Falco, ejecuta una prueba controlada desde una terminal interactiva:

```bash
sudo docker exec -it uts-portal sh -c 'echo prueba-falco'
sudo docker logs --since=2m uts-falco 2>&1 | grep -F 'container_name=uts-portal'
```

La segunda línea debe mostrar una alerta `A shell was spawned in a container with an attached terminal` con `command=sh -c echo prueba-falco`. Captura también el resultado de `sudo docker compose -f compose.yaml -f falco.compose.yaml ps -a` para asociar portal y sensor a la misma VM.

### Salida JSON local para la integración con Wazuh

La configuración versionada `deploy/ubuntu/falco.compose.yaml` añade una salida JSON línea por línea en `falco-logs/events.jsonl` y mantiene la salida de Docker. El directorio local está excluido de Git porque las alertas pueden contener comandos y rutas. Después de actualizar el clon en la VM:

```bash
sudo install -d -m 0700 falco-logs
sudo docker compose -f compose.yaml -f deploy/ubuntu/falco.compose.yaml config --quiet
sudo docker logs uts-falco > ~/falco-compose-previo.log 2>&1
sudo docker compose -f compose.yaml -f deploy/ubuntu/falco.compose.yaml up -d falco
sudo docker exec -it uts-portal sh -c 'echo prueba-falco-json'
sudo python3 scripts/verificar_falco_json.py
```

Usa la ruta versionada `deploy/ubuntu/falco.compose.yaml`; la copia `falco.compose.yaml` extraída anteriormente en la raíz corresponde a la configuración previa. `up -d falco` recrea solo el sensor cuando cambia su configuración. Antes de continuar, verifica que el portal sigue saludable con `curl -fsS http://127.0.0.1:8080/health`. Falco no rota automáticamente su archivo de salida: mantén el piloto supervisado y revisa el tamaño con `sudo du -h falco-logs/events.jsonl`. La integración Falco → Wazuh manager ya produjo una alerta real `100200` en esta VM; consulta [fase H](../../docs/fase-h-preparacion-wazuh-falco.md).

### Prueba del manager Wazuh sin indexer ni dashboard

La VM no tiene los recursos mínimos del stack oficial completo. El archivo `deploy/ubuntu/wazuh-manager.compose.yaml` permite una **prueba acotada del manager** en la misma VM, sin puertos publicados. Su imagen deriva de `wazuh/wazuh-manager:4.14.9` y omite Filebeat porque no se despliega un indexer. El manager lee el archivo JSON de Falco en modo de solo lectura y aplica la regla local `100200`. Preparación:

```bash
sudo chgrp 999 falco-logs falco-logs/events.jsonl
sudo chmod 2750 falco-logs
sudo chmod 640 falco-logs/events.jsonl
sudo docker compose -f compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml config --quiet
sudo docker compose -f compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml up -d --build wazuh_manager
```

El grupo `999` corresponde al grupo `wazuh` en esta versión de la imagen; los permisos permiten leer el archivo sin hacerlo público para otros usuarios de la VM. Antes de activar Wazuh, comprueba que sigan quedando varios GiB libres en disco y memoria; si el manager presiona el sistema, detenlo con `sudo docker compose -f compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml stop wazuh_manager`. Esto conserva los volúmenes y deja el portal y Falco funcionando.

Cuando el manager esté listo, valida primero la regla con una línea Falco ya registrada:

```bash
sudo grep -F 'prueba-falco-json' falco-logs/events.jsonl | tail -n 1 | sudo docker exec -i uts-wazuh-manager /var/ossec/bin/wazuh-logtest
```

Esa es una **prueba de regla por reproducción**, no una alerta recibida en vivo. Para la evidencia real, genera un nuevo evento después de arrancar el manager y comprueba `alerts.json`:

```bash
sudo docker exec -it uts-portal sh -c 'echo prueba-falco-wazuh'
sudo python3 scripts/verificar_wazuh_falco.py
```

El verificador solo muestra la regla y el marcador de prueba; no imprime el contenido completo de los registros. La regla `100200` para un evento Falco nuevo quedó confirmada en `alerts.json` a las 01:17:48 UTC del 22 de octubre de 2026.

### Auditoría del portal hacia el mismo manager

El portal escribe `audit.jsonl` en el volumen `audit_logs`. El manager lo monta en modo de solo lectura y aplica las reglas `100100`–`100103`, además de la regla Falco `100200`. Las alertas nuevas `100100` y `100101` quedaron verificadas en Ubuntu a las 01:39:43 UTC del 22 de octubre de 2026. El procedimiento, permisos, prueba y límites están en [fase I](../../docs/fase-i-auditoria-wazuh-ubuntu.md). Para la copia clonada del repositorio usa siempre `-f compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml`.

Conserva los volúmenes: para detener usa `docker compose stop`; no uses `docker compose down -v`. La imagen del portal conserva el hallazgo alto de `zlib` documentado en el escaneo previo; subirla a Docker Hub no corrige esa vulnerabilidad.
