# Fase I: auditoría del portal hacia Wazuh en Ubuntu

Estado: **configuración preparada; falta validación en vivo en la VM**.

## Objetivo

El manager de Ubuntu ya procesa el JSON de Falco con la regla `100200`. Esta fase agrega el volumen `audit_logs` del portal al mismo manager, en modo de solo lectura, para aplicar las reglas `100100`–`100103` a sus eventos de autenticación, autorización y disponibilidad. El portal y PostgreSQL no se recrean durante la incorporación del manager.

## Cambios de arquitectura

- `deploy/ubuntu/wazuh-manager.compose.yaml` monta `audit_logs:/var/log/uts:ro` y el archivo de reglas `wazuh-portal-rules.xml`.
- `deploy/ubuntu/wazuh-manager.conf` recoge `/var/log/uts/audit.jsonl*` como JSON con la etiqueta `@source=uts-portal`. El comodín incluye archivos rotados.
- El directorio y los archivos de auditoría se comparten con el grupo numérico `999` de Wazuh. El portal sigue siendo propietario y puede escribir; el manager solo lee. El contenedor no publica puertos de Wazuh.
- `scripts/verificar_wazuh_portal_ubuntu.py` ejecuta la prueba funcional existente y busca **alertas posteriores al inicio** de la prueba para `login_failed` y `access_denied`. Solo imprime identificadores, niveles y horas.

## Aplicación en la VM

Desde SSH, en `~/cwpp-cloud-2026`, ejecuta una línea a la vez y detente si alguna falla:

```bash
cd ~/cwpp-cloud-2026 && git pull --ff-only && sudo docker compose -f compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml config --quiet
```

```bash
cd ~/cwpp-cloud-2026 && sudo docker exec -u 0 uts-portal sh -c 'chgrp 999 /var/log/uts /var/log/uts/audit.jsonl* && chmod 2750 /var/log/uts && chmod 640 /var/log/uts/audit.jsonl*' && sudo docker compose -f compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml up -d --no-deps --force-recreate wazuh_manager
```

```bash
cd ~/cwpp-cloud-2026 && sleep 20 && sudo docker exec uts-wazuh-manager /var/ossec/bin/wazuh-control status && sudo docker compose -f compose.yaml -f deploy/ubuntu/falco.compose.yaml -f deploy/ubuntu/wazuh-manager.compose.yaml ps -a
```

```bash
cd ~/cwpp-cloud-2026 && sudo python3 scripts/verificar_wazuh_portal_ubuntu.py && curl -fsS http://127.0.0.1:8080/health
```

La prueba solo usa cuentas y datos de demostración. Debe mostrar alertas **100100** y **100101** nuevas en `alerts.json`, además de `status: ok` y `database: connected`. La coincidencia de `wazuh-logtest` por sí sola no demostraría lectura del volumen. Si no aparecen, consultar `sudo docker logs --tail=80 uts-wazuh-manager` y `sudo docker exec -u 0 uts-wazuh-manager ls -ld /var/log/uts /var/log/uts/audit.jsonl` sin imprimir el contenido del archivo.

## Evidencia y límites

Captura `28-wazuh-auditoria-ubuntu.png` con las reglas 100100/100101, horas y salud del portal. Captura `29-ubuntu-arquitectura-integrada.png` con los cuatro contenedores activos. Guarda ambas en `docs/evidencias/capturas/`, fuera de Git. Las reglas 100102/100103 quedan instaladas, pero una alerta de disponibilidad en vivo requeriría una nueva caída controlada de PostgreSQL; no se atribuirá sin ejecutar esa prueba.

La lectura del volumen de auditoría del portal **no equivale a auditoría directa de PostgreSQL**. Tampoco hay indexer ni dashboard en la VM. El archivo JSON de Falco requiere vigilancia de tamaño y retención antes de una operación prolongada.
