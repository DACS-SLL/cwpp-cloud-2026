# Fase I: auditoría del portal hacia Wazuh en Ubuntu

Estado: **integración de auditoría validada en vivo en la VM Ubuntu**.

## Objetivo

El manager de Ubuntu ya procesa el JSON de Falco con la regla `100200`. Esta fase agrega el volumen `audit_logs` del portal al mismo manager, en modo de solo lectura, para aplicar las reglas `100100`–`100103` a sus eventos de autenticación, autorización y disponibilidad. El portal y PostgreSQL no se recrean durante la incorporación del manager.

## Cambios de arquitectura

- `deploy/ubuntu/wazuh-manager.compose.yaml` monta `audit_logs:/var/log/uts:ro` y el archivo de reglas `wazuh-portal-rules.xml`.
- `deploy/ubuntu/wazuh-manager.conf` recoge `/var/log/uts/audit.jsonl*` como JSON con la etiqueta `@source=uts-portal`. El comodín incluye archivos rotados.
- El directorio y los archivos de auditoría se comparten con el grupo numérico `999` de Wazuh. El portal sigue siendo propietario y puede escribir; el manager solo lee. El contenedor no publica puertos de Wazuh.
- `scripts/verificar_wazuh_portal_ubuntu.py` ejecuta la prueba funcional existente y busca **alertas posteriores al inicio** de la prueba para `login_failed` y `access_denied`. Solo imprime identificadores, niveles y horas.

## Resultado observado

El 22 de octubre de 2026 a las **01:39:43 UTC**, la prueba de roles generó en `/var/ossec/logs/alerts/alerts.json` dos alertas nuevas: `100100`, nivel 7, para `login_failed` y `100101`, nivel 6, para `access_denied`. La consulta posterior a `/health` devolvió `{"database":"connected","status":"ok"}`. Este resultado valida la lectura del volumen de auditoría del portal por el manager de **la misma VM** que procesa Falco. La evidencia depurada está en [wazuh-portal-ubuntu-verificacion.json](evidencias/wazuh-portal-ubuntu-verificacion.json) y la captura local es `docs/evidencias/capturas/28-wazuh-auditoria-ubuntu.png`.

Una muestra posterior mostró los cuatro contenedores activos, portal y base `healthy`, manager con **404,8 MiB**, Ubuntu con **2,4 GiB** de memoria disponible y **9,0 GB** de disco libre. La captura local `29-ubuntu-arquitectura-integrada.png` conserva esa muestra. Son valores instantáneos, no una medición de carga sostenida.

## Aplicación en la VM

Desde SSH, en `~/cwpp-cloud-2026`, ejecuta una línea a la vez y detente si alguna falla:

```bash
cd ~/cwpp-cloud-2026 && git pull --ff-only && sudo docker compose -f compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml config --quiet
```

```bash
cd ~/cwpp-cloud-2026 && sudo docker volume inspect uts-cwpp-ubuntu_audit_logs >/dev/null && sudo docker run --rm --network none --entrypoint sh -v uts-cwpp-ubuntu_audit_logs:/var/log/uts postgres:17-alpine -c 'chgrp 999 /var/log/uts /var/log/uts/audit.jsonl* && chmod 2750 /var/log/uts && chmod 640 /var/log/uts/audit.jsonl*' && sudo docker compose -f compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml up -d --no-deps --force-recreate wazuh_manager
```

```bash
cd ~/cwpp-cloud-2026 && sleep 60 && sudo docker ps --filter name=uts- --format 'table {{.Names}}\t{{.Status}}' && sudo docker exec uts-wazuh-manager /var/ossec/bin/wazuh-control status
```

```bash
cd ~/cwpp-cloud-2026 && sudo python3 scripts/verificar_wazuh_portal_ubuntu.py && curl -fsS http://127.0.0.1:8080/health
```

La prueba solo usa cuentas y datos de demostración. Debe mostrar alertas **100100** y **100101** nuevas en `alerts.json`, además de `status: ok` y `database: connected`. La coincidencia de `wazuh-logtest` por sí sola no demostraría lectura del volumen. Si no aparecen, consultar `sudo docker logs --tail=80 uts-wazuh-manager` y `sudo docker exec -u 0 uts-wazuh-manager ls -ld /var/log/uts /var/log/uts/audit.jsonl` sin imprimir el contenido del archivo. El portal tiene `cap_drop: ALL`; por eso el cambio de grupo se hace con un contenedor auxiliar temporal, sin red, y no mediante `docker exec -u 0 uts-portal`. El primer inicio del manager tardó más de 20 segundos; `wazuh-control status` también puede devolver código distinto de cero por servicios opcionales detenidos, aunque `analysisd` y `logcollector` estén activos.

## Evidencia y límites

Las capturas `28-wazuh-auditoria-ubuntu.png` y `29-ubuntu-arquitectura-integrada.png` ya están guardadas en `docs/evidencias/capturas/`, fuera de Git. Las reglas 100102/100103 quedan instaladas, pero una alerta de disponibilidad en vivo requeriría una nueva caída controlada de PostgreSQL; no se atribuirá sin ejecutar esa prueba.

La lectura del volumen de auditoría del portal **no equivale a auditoría directa de PostgreSQL**. Tampoco hay indexer ni dashboard en la VM. El archivo JSON de Falco requiere vigilancia de tamaño y retención antes de una operación prolongada.
