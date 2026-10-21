# Preparación de Wazuh para el piloto UTS

**Estado (21 de octubre de 2026):** certificados, credenciales locales e imágenes preparados. Indexer y manager detectaron dos eventos reales del portal. En una prueba separada, indexer y dashboard permitieron el ingreso a la interfaz. Los tres componentes están detenidos por presión de RAM; el portal y PostgreSQL siguen saludables. Ver `docs/fase-d-wazuh.md` y `docs/evidencias/wazuh-alertas-verificadas.json`.

La carpeta `upstream/` procede del repositorio oficial `wazuh/wazuh-docker`, etiqueta `v4.14.9` (commit local `56ece95`). Su modelo `single-node` se adaptó para este piloto:

- Dashboard publicado solo en `https://localhost:8443`.
- Puertos de agentes 1514/1515 enlazados solo a `127.0.0.1`; indexer y API no se publican en Windows.
- Manager monta `uts-cwpp_audit_logs` en modo lectura y tiene un `<localfile>` JSON para `/var/log/uts/audit.jsonl*`.
- `docker compose config --quiet` pasó. Certificados y arranque permitieron dos pruebas controladas; el manager registró alertas reales `100100` y `100101`. La visualización de esas alertas en el dashboard sigue pendiente.

El portal ya escribe eventos de auditoría en ese volumen con rotación (máximo aproximado: 12 MB). Tras recrear el portal dos veces y repetir las pruebas se verificaron 60 eventos acumulados de seis tipos: `auth_required`, `login_failed`, `login_success`, `access_denied`, `data_access` y `logout`. Gunicorn quedó con un worker para evitar rotación concurrente del archivo. Esto demuestra persistencia y producción de logs, **no** la detección ni visualización por Wazuh.

Se prepararon cuatro reglas en `config/wazuh_cluster/uts_portal_rules.xml` para ingresos fallidos, accesos denegados, fallos de disponibilidad y fallos de consulta. `wazuh-logtest` y el archivo de alertas verificaron las dos primeras con eventos reales. Las reglas de disponibilidad `100102` y consulta `100103` coincidieron en `wazuh-logtest` con eventos sintéticos; su alerta real durante una caída todavía no se ha demostrado.

## Requisitos antes de arrancar

1. Liberar memoria en Windows. Después de reiniciar WSL y reactivar el portal quedaban entre 0,75 y 0,97 GiB libres. No arrancar el stack con ese margen.
2. El límite global de WSL ya se estableció en 9 GB mediante `%UserProfile%\.wslconfig`; Docker reportó 9 371 779 072 bytes utilizables (aproximadamente 8,73 GiB). El portal y la base se reactivaron y quedaron saludables. Conservar este valor mientras se evalúa Wazuh; revertirlo solo si se abandona el despliegue.
3. C: tenía 52,68 GiB libres tras generar certificados, cerca del mínimo de 50 GB para imágenes y datos. El disco virtual de Docker está en C:, no en D:.
4. `vm.max_map_count` dio `262144` después del reinicio.
5. Se ejecutó el generador oficial y existen los 12 archivos esperados en `single-node/config/wazuh_indexer_ssl_certs/`. El generador terminó con código 0, aunque imprimió un aviso interno `find: command not found`; falta comprobar certificados al iniciar los servicios.
6. Se prepararon contraseñas propias en archivos ignorados por Git y se descargaron las tres imágenes. El manager recogió dos alertas reales. Al operar solo indexer y manager, Windows cayó a 0,12 GiB libres, así que ambos se detuvieron. El dashboard requiere más recursos antes de intentarlo.

No ejecutar `docker compose down -v` en ninguno de los proyectos. Los volúmenes de PostgreSQL, auditoría y Wazuh deben conservarse.

## Fuentes

- [Despliegue oficial de Wazuh en Docker](https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html).
- [Cambio de contraseñas predeterminadas](https://documentation.wazuh.com/current/deployment-options/docker/changing-default-password.html).
- [Recolección de archivos JSON con localfile](https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/localfile.html).
- [Sintaxis de reglas Wazuh](https://documentation.wazuh.com/current/user-manual/ruleset/ruleset-xml-syntax/rules.html).
- [Límite de memoria y reinicio de WSL](https://learn.microsoft.com/en-us/windows/wsl/wsl-config).
