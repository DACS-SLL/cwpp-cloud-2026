# Capturas de infraestructura para el parcial

Usa **Win + Shift + S** y guarda las imágenes en `docs/evidencias/capturas/` con los nombres sugeridos. Deja visible el comando, su salida y, si es posible, la fecha de Windows. Recorta contraseñas, `.env`, `credenciales_portal.txt` y tokens de sesión. El portal debe mostrar solo datos de prueba.

| Archivo sugerido | Dónde y qué capturar | Qué demuestra |
| --- | --- | --- |
| `01-contenedores.png` | Docker Desktop → **Containers**, proyecto `uts-cwpp`: `uts-database` y `uts-portal` en ejecución; o PowerShell con `docker compose ps -a`. | Separación aplicación/base, estado saludable y puerto local 8080. |
| `02-redes-volumen.png` | PowerShell en el proyecto: ejecutar `./scripts/evidencia_infra.ps1` y encuadrar la sección **Redes y volumen**. | Base y portal comparten `uts_internal`; solo el portal está en `portal_access`; volumen PostgreSQL persistente. |
| `03-configuracion-portal.png` | El mismo script, sección **Restricciones del portal**. | UID 10001, raíz de solo lectura, sin modo privilegiado, capacidades eliminadas, límites de procesos y memoria. |
| `04-salud-datos.png` | El mismo script, sección **Salud HTTP y PostgreSQL**. | `/health` conectado y recuentos 20 estudiantes, 7 cursos, 60 matrículas sin mostrar registros personales. |
| `05-roles.png` | Navegador en `http://localhost:8080`: ingresar como `estudiante_demo`; capturar inicio con rol y la vista de matrículas con 3 registros. | Restricción de registros por identidad de prueba. No captures el archivo de contraseñas. |
| `06-acceso-denegado.png` | Con esa sesión de estudiante, abrir `http://localhost:8080/estudiantes`; capturar HTTP 403. | Autorización aplicada por el servidor. |
| `07-auditoria.png` | PowerShell: `docker compose logs --tail=80 portal`; encuadrar una línea JSON `access_denied` y otra `data_access`. | Trazabilidad de accesos sin contraseñas ni contenido académico. |
| `08-vulnerabilidades.png` | Abrir `docs/evidencias/scout-portal-actual.md` en vista previa Markdown o mostrar el resumen de Docker Scout. | Resultado de análisis de la imagen actual. Registrar el hallazgo como resultado del escáner, sin asumir explotación. |
| `09-consumo.png` | Script de evidencia, sección **Consumo actual**, o Docker Desktop → **Containers** → métricas. | Línea base de CPU y RAM para comparar con fases posteriores. |
| `10-arquitectura.png` | Abrir `docs/evidencias/arquitectura-actual.png` o `docs/arquitectura-actual.svg`. El PNG ya está listo para insertar en el informe. | Diagrama visible del recorrido navegador → portal → base, redes y volumen. |

Si quieres abrir una ventana que **permanezca visible para la captura**, haz doble clic en `scripts/abrir_evidencia_infra.cmd`. El lanzador muestra la salida, la guarda en `docs/evidencias/infraestructura.txt` y espera una tecla antes de cerrar. Si ya tienes PowerShell abierto en `C:\Cloud_parcial\uts-cwpp`, también puedes ejecutar:

```powershell
.\scripts\evidencia_infra.ps1
```

El lanzador aplica la excepción de política de ejecución solo a ese proceso. No abras el `.ps1` con doble clic porque Windows puede cerrar su consola al terminar. No uses `docker compose config` sin `--quiet` para una captura: incluiría valores de entorno sensibles.

## Capturas pendientes de Wazuh y Falco

**Actualización fase F:** Falco ya produjo dos alertas reales del portal en Ubuntu VirtualBox. Las capturas locales `16-ubuntu-compose-smoke.png`, `17-portal-ubuntu-windows.png`, `18-falco-modern-bpf-iniciado.png`, `19-falco-consulta-inicial.png` y `20-falco-alerta-portal.png` están en `docs/evidencias/capturas/`. Para RF-04, usa **20** como evidencia principal: contiene la hora, la descripción de la alerta, `container_name=uts-portal` y la imagen. Usa **18** para mostrar que Falco cargó la fuente `syscall` con modern BPF. La captura **19** muestra el comando de prueba. Los detalles y límites están en [fase F](fase-f-falco-ubuntu.md).

Como evidencia de las fases previas, puedes capturar `docker volume ls --filter name=uts-cwpp_audit_logs` junto a `docker compose ps -a`, y `docker compose logs --tail=30 portal` mostrando un evento JSON. Cuando haya recursos suficientes, captura los tres componentes Wazuh en Docker Desktop, el dashboard con una alerta verificable, la correlación con el log del portal y el consumo adicional. La prueba independiente de Falco sobre el portal de la VM Ubuntu se completó en fase F; una captura del sensor encendido sin alerta atribuible al portal no demuestra detección.

**Próxima captura (`21-falco-compose-reproducible.png`):** después de arrancar Falco desde `falco.compose.yaml` en Ubuntu, deja visibles `sudo docker compose -f compose.yaml -f falco.compose.yaml ps -a` y `sudo docker logs --since=2m uts-falco 2>&1 | grep -F 'container_name=uts-portal'`. Genera primero el evento con `sudo docker exec -it uts-portal sh -c 'echo prueba-falco'`. La captura debe mostrar `uts-falco` en ejecución y una alerta nueva con `container_name=uts-portal`; guarda el archivo en `docs/evidencias/capturas/`, fuera de Git.

La preparación de Wazuh ya permite una captura adicional: en PowerShell muestra `docker info --format '{{.MemTotal}}'` (valor actual: `9371779072`) y `docker run --rm alpine:3.20 cat /proc/sys/vm/max_map_count` (valor: `262144`). Para documentar los certificados, en `security/wazuh/upstream/single-node` ejecuta `Get-ChildItem config/wazuh_indexer_ssl_certs -Name` y captura **solo los nombres**, sin abrir los archivos `*-key.pem` ni `root-ca.key`. Estos datos muestran requisitos previos, no funcionamiento de Wazuh.

La prueba controlada ya generó dos alertas reales. Abre `docs/evidencias/wazuh-alertas-verificadas.json` y captura las reglas `100100` y `100101` con sus fechas y eventos. La captura aportada del dashboard está guardada en `docs/evidencias/capturas/15-dashboard-api-offline.png`: demuestra ingreso a la interfaz y muestra que la API del manager estaba offline. No la presentes como evidencia de monitoreo completo. Lee `docs/fase-d-wazuh.md` para describir el alcance.

**Nueva captura RF-06:** abre `docs/evidencias/disponibilidad-postgresql.json` en VS Code. Encuadra `http` (503 durante la caída, 200 tras recuperación) y los eventos `service_unavailable` y `database_query_failed`. Después, en PowerShell desde `C:\Cloud_parcial\uts-cwpp`, ejecuta `docker compose ps -a` y captura los dos servicios `healthy`. Ambas capturas juntas prueban interrupción detectada y recuperación; los eventos todavía no son alertas de Wazuh.

Las reglas Wazuh `100102` y `100103` también coincidieron con eventos **sintéticos** en `wazuh-logtest` (niveles 10 y 5). Si se usa esa pantalla, rotularla como prueba de reglas y no como alerta real del incidente. Consulta `docs/fase-e-disponibilidad.md`.

## Captura de la validación actual

Para evidenciar la línea base, abre `docs/evidencias/metricas-base.json` en VS Code y captura la fecha UTC, `scope` y las tres rutas con sus medianas, percentiles 95 y cero errores. Como alternativa, ejecuta `python scripts/medir_piloto.py` en PowerShell y captura solo el resumen impreso. Esta prueba genera consultas de lectura y eventos de auditoría; no instala Wazuh ni modifica la base. El alcance y los límites están explicados en `docs/fase-c-validacion.md`.
