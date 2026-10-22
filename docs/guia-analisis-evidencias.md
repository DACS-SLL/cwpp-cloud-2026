# Guía para revisar las imágenes del piloto CWPP UTS

## Cómo usarla en el informe grupal

Las capturas originales están en `docs/evidencias/capturas/` **solo en la PC del proyecto** y están excluidas de Git. Los tres diagramas PNG —general, Ubuntu y Windows— y los resultados JSON depurados sí están versionados. El DOCX del avance incorpora copias de las capturas 27–29 como anexo. El integrante que prepare el informe debe recibir las capturas locales por un canal acordado, revisar cada una y añadir un pie de figura con: entorno, comando o pantalla, fecha si es visible, resultado observable y límite. No se debe inferir un estado actual a partir de una captura histórica.

Para cada imagen: (1) lee el comando o URL y el nombre del equipo; (2) identifica el componente; (3) compara el resultado con el JSON o documento de fase; (4) anota si es **estado**, **prueba de regla**, **alerta real**, **métrica puntual** o **diseño**; (5) verifica que no aparezcan contraseñas, `.env`, claves o registros académicos reales. Recorta únicamente elementos privados o irrelevantes y conserva el original local. No alteres números, fechas, estados ni mensajes.

| Nº y archivo local | Qué se observa y cómo interpretarlo | Uso recomendado / límite |
| --- | --- | --- |
| 01 `01-contenedores.png` | Portal y PostgreSQL en Docker Desktop. | Estado inicial de Windows; no prueba Wazuh ni Falco. |
| 02 `02-redes-volumen.png` | Redes y volumen de datos. | Separación lógica y persistencia; no prueba aislamiento absoluto. |
| 03–04 | No existen capturas locales con esos números. | No crear pies de figura ni completar el hueco con una imagen distinta. |
| 05 `05-roles.png` | Consulta con usuario de prueba y rol. | Relacionar con control de acceso; ocultar cualquier credencial. |
| 06 `06-acceso-denegado.png` | Vista denegada a rol estudiante. | Evidencia de HTTP 403; no confundir con alerta Wazuh. |
| 07 `07-auditoria.png` | Línea JSON de auditoría del portal. | Origen de `access_denied`/`data_access`; no equivale a auditoría directa de PostgreSQL. |
| 08 `08-vulnerabilidades.png` | Resultado de Docker Scout para imagen anterior. | Informar hallazgo alto de zlib tal como lo reporta el escáner; no afirmar explotación. |
| 09 `09-consumo.png` | CPU y memoria de la línea base. | Muestra puntual, no promedio ni benchmark. |
| 10 `10-arquitectura.png` | Diagrama temprano de Windows. | Usar como evolución histórica; para la arquitectura final usar los dos PNG versionados. |
| 11 `11-metricas-base.png` | Latencias y errores de una prueba de lectura. | Citar tamaño y condiciones del piloto; no prometer rendimiento de producción. |
| 12 `12-alertas-verificadas.png` | Alertas Wazuh 100100 y 100101 en Windows. | Alertas reales de auditoría del portal en esa sesión. |
| 13 `13-componentes-wazuh.png` | Componentes Wazuh visibles. | Distinguir procesos iniciados de integración completa. |
| 14 `14-docker-wazuh.png` | Contenedores Wazuh de una sesión de Windows. | No mezclar temporalmente con la captura 15 ni afirmar stack completo estable. |
| 15 `15-dashboard-api-offline.png` | Dashboard accesible con API del manager offline. | Prueba de acceso a interfaz, **no** de monitoreo completo. |
| 16 `16-ubuntu-compose-smoke.png` | Portal/base saludables y smoke test en Ubuntu. | Funcionamiento funcional en la VM. |
| 17 `17-portal-ubuntu-windows.png` | Portal de la VM visto desde Windows vía NAT. | Acceso local `localhost:18080`; es el front anterior al rediseño. |
| 18 `18-falco-modern-bpf-iniciado.png` | Fuente `syscall` de Falco con modern BPF. | Sensor iniciado en Ubuntu; por sí sola no prueba una detección. |
| 19 `19-falco-consulta-inicial.png` | Comando de estímulo controlado. | Emparejar con 20; el comando solo no es alerta. |
| 20 `20-falco-alerta-portal.png` | Falco atribuye shell a `uts-portal`. | Evidencia principal de detección de runtime en Ubuntu. |
| 21 `21-falco-compose-reproducible.png` | Falco junto a portal/base bajo Compose. | Estado de despliegue reproducible. |
| 22 `22-falco-compose-alerta.png` | Nuevo evento `prueba-falco-compose`. | Detección después de pasar Falco a Compose. |
| 23 `23-consumo-ubuntu-falco.png` | `docker stats` y `free -h`. | Muestra de recursos previa al manager Wazuh. |
| 24 `24-falco-json-local.png` | JSON local de Falco con regla, prioridad y contenedor. | Entrada preparada para Wazuh; no rotular como alerta Wazuh. |
| 25 `25-wazuh-manager-ubuntu.png` | Cuatro contenedores y recursos en Ubuntu. | Estado puntual del manager; revisar hora y memoria. |
| 26 `26-wazuh-logtest-falco.png` | `Phase 3` y regla 100200 nivel 8. | **Prueba de regla** con evento reproducido; no alerta recibida en vivo. |
| 27 `27-wazuh-alerta-falco-real.png` | Verificador halla 100200 en `alerts.json` y `/health` correcto. | Evidencia principal Falco → Wazuh en vivo. |
| 28 `28-wazuh-auditoria-ubuntu.png` | Nuevas 100100/100101 y portal saludable. | Evidencia principal auditoría del portal → Wazuh en vivo. |
| 29 `29-ubuntu-arquitectura-integrada.png` | Cuatro servicios activos, portal/base healthy, memoria/disco. | Estado de la VM y consumo puntual; los valores no representan carga sostenida. |

También existen `base_datos_construida.png`, `docker_creado.png` y `estructura_carpetas.png` como apoyo visual. Verifica su fecha y relación con el entorno antes de usarlas; sus nombres no bastan para atribuir controles de seguridad.

Las imágenes versionadas [prototipo-inicio-nuevo.png](evidencias/prototipo-inicio-nuevo.png) y [prototipo-ingreso-nuevo.png](evidencias/prototipo-ingreso-nuevo.png) son **previsualizaciones del rediseño** tomadas en un contenedor aislado con configuración ficticia. Sirven para mostrar el nuevo diseño del front, pero no demuestran que la VM ya haya actualizado su contenedor ni que PostgreSQL estuviera conectado en esa sesión. Para probar el despliegue final, reconstruye el portal en Ubuntu y toma una nueva captura con el commit y la salud de los servicios.

## Selección mínima para el integrante 4

1. Presenta [arquitectura Windows](evidencias/arquitectura-windows.png) como trayectoria de las pruebas iniciales y [arquitectura Ubuntu](evidencias/arquitectura-ubuntu.png) como piloto integrado. No los combines en una topología simultánea.
2. Para implementación y permisos usa 16, 18 y 21. Para resultados de seguridad usa 20, 27 y 28. Para uso de recursos usa 23 y 29, etiquetando ambas como muestras instantáneas.
3. Si incluyes 26, escribe “validación de regla con `wazuh-logtest`”; acompáñala de 27 para demostrar alerta real. Si incluyes 15, indica “manager API offline”.
4. En el pie de 28 escribe: “Ubuntu; prueba de roles; Wazuh manager registró `login_failed` (100100, nivel 7) y `access_denied` (100101, nivel 6); `/health` devolvió `ok`”. En el pie de 27 escribe: “Ubuntu; evento nuevo de Falco asociado a `uts-portal`; Wazuh registró regla 100200, nivel 8”.
5. Para un lector sin capturas originales, usa [resumen JSON Falco → Wazuh](evidencias/wazuh-falco-ubuntu-verificacion.json), [resumen JSON portal → Wazuh](evidencias/wazuh-portal-ubuntu-verificacion.json) y [fase I](fase-i-auditoria-wazuh-ubuntu.md). Son evidencias depuradas, no sustitutos de la captura original.

## Qué no afirmar

- La VM Ubuntu **no** incluye indexer ni dashboard Wazuh. La captura de dashboard de Windows tiene la API del manager desconectada.
- Falco en Ubuntu no observa automáticamente los contenedores de Docker Desktop de Windows.
- Las reglas 100102/100103 no se observaron como alertas reales en la VM; en Windows se verificaron con eventos sintéticos. La caída real de PostgreSQL se documentó por HTTP y auditoría del portal.
- El análisis de imagen de Docker Scout no demuestra explotación ni corrección del hallazgo.
- Las capturas previas del portal no muestran el front nuevo. Tras reconstruir `uts-cwpp-portal:local`, captura de nuevo inicio, ingreso y tabla e identifica el commit usado.
