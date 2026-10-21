# Fase C: validación del piloto disponible

> Este informe conserva la línea base anterior a Wazuh. Las pruebas posteriores están en `docs/fase-d-wazuh.md` y `docs/fase-e-disponibilidad.md`.

Fecha de medición: 21 de octubre de 2026 (UTC). El alcance de esta línea base es el portal y PostgreSQL en Docker Desktop local, antes de probar Wazuh.

## Resultado de las pruebas

| Criterio | Evidencia disponible | Estado |
| --- | --- | --- |
| RF-01: accesos y autenticación | `scripts/smoke_portal.py` validó ingreso, denegación por rol y cierre de sesión. Los eventos `login_failed`, `access_denied` y `data_access` se registran como JSON persistente. | Validado en el portal en esta línea base; Wazuh detectó después los dos primeros. |
| RF-02: vulnerabilidades | Docker Scout analizó `uts-cwpp-portal:latest`: 1 hallazgo alto en `zlib`, 0 críticos. | Análisis realizado; hallazgo abierto. |
| RF-03: endurecimiento | Portal con UID/GID 10001, raíz de solo lectura, capacidades eliminadas, `no-new-privileges`, límites de procesos y RAM. | Validado para el portal; no se atribuye el mismo endurecimiento a PostgreSQL. |
| RF-04: comportamiento en ejecución | Falco todavía no está instalado ni se ha probado su visibilidad del kernel de Docker Desktop. | Pendiente. |
| RF-05: actividad de datos | El portal registra consultas autorizadas como `data_access` con recurso y número de filas, sin contenido académico. | Parcial: no es auditoría directa del motor PostgreSQL. |
| RF-06: disponibilidad | `/health` comprueba la conexión a PostgreSQL. Ambos contenedores estaban `healthy` en la evidencia de infraestructura. | Estado normal validado aquí; la simulación de caída posterior consta en fase E. |

En esta línea base no se calcularon precisión, falsos positivos, MTTD ni MTTR. La prueba posterior de Wazuh observó dos alertas reales, pero todavía no permite estimar esas métricas con rigor.

## Línea base de latencia (RNF-05)

Se hicieron 30 solicitudes HTTP secuenciales por ruta desde Windows a `localhost:8080`, con una sesión de administrador de demostración para las vistas protegidas. Cada tiempo incluye ida y vuelta HTTP y lectura de la respuesta. No es una prueba de carga concurrente ni mide usuarios remotos. Hubo una sola ejecución, sin Wazuh ni Falco.

| Ruta | Respuestas inesperadas | Mediana | Percentil 95 | Máximo |
| --- | ---: | ---: | ---: | ---: |
| `/health` | 0/30 | 17,49 ms | 36,03 ms | 42,04 ms |
| `/cursos` | 0/30 | 19,99 ms | 34,77 ms | 34,95 ms |
| `/matriculas` | 0/30 | 22,13 ms | 38,88 ms | 47,86 ms |

Datos reproducibles: `python scripts/medir_piloto.py` guarda `docs/evidencias/metricas-base.json`. El script solo imprime agregados y el archivo no contiene credenciales ni datos académicos. La evidencia `infraestructura.txt` anterior a esta medición registró aproximadamente 46,39 MiB para el portal y 32,59 MiB para PostgreSQL con `docker stats --no-stream`; son muestras puntuales, no promedios ni consumo del stack CWPP completo.

## Evidencia para el informe

- `docs/evidencias/metricas-base.json`: valores de latencia y fecha UTC.
- `docs/evidencias/infraestructura.txt`: contenedores, salud, redes, volumen, restricciones y consumo puntual.
- `docs/evidencias/scout-portal-actual.md`: resultado del análisis de vulnerabilidades.
- `docs/evidencias/arquitectura-actual.png`: arquitectura efectivamente implementada.
- `docs/capturas-evidencia.md`: ubicación y contenido de las capturas de pantalla.

La comparación de rendimiento con todos los componentes simultáneos sigue pendiente por los límites de RAM documentados en fase D.
