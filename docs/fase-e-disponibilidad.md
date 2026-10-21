# Fase E: caída controlada de PostgreSQL y evaluación de Falco

Fecha: 21 de octubre de 2026 (UTC). Todas las pruebas se ejecutaron en este mismo equipo.

## RF-06: disponibilidad y recuperación

Se ejecutó `python scripts/probar_disponibilidad.py`. El programa confirmó que portal y base estaban encendidos, inició una sesión de demostración, detuvo **solo** `uts-database`, consultó `/health` y `/cursos`, y reinició la base en un bloque `finally`. Luego esperó la recuperación de ambos endpoints. Los volúmenes no se eliminaron.

| Comprobación | Resultado observado |
| --- | ---: |
| `/health` durante caída | HTTP 503 |
| `/cursos` autenticado durante caída | HTTP 503 |
| `/health` tras reinicio | HTTP 200 |
| `/cursos` autenticado tras reinicio | HTTP 200 |

El log persistente registró tres eventos `service_unavailable` y un `database_query_failed` durante la ventana de prueba. La evidencia sin usuarios, IP ni contenido académico está en `docs/evidencias/disponibilidad-postgresql.json`. Al cierre, `docker compose ps -a` mostró ambos contenedores `healthy`.

Después del reinicio, `python scripts/smoke_portal.py` volvió a pasar para los tres roles de demostración: ingreso, permisos, consultas y salida. Esto comprobó que la base y los datos de prueba siguieron disponibles.

Esto verifica la señal local de indisponibilidad y la recuperación, pero **no** una alerta Wazuh real de las reglas `100102`/`100103`: el manager permaneció detenido durante la caída. Posteriormente, con **solo** el manager encendido, `wazuh-logtest` procesó eventos JSON sintéticos de ambos tipos. La regla `100102` coincidió con nivel 10 y la `100103` con nivel 5; ambas indicaron `Alert to be generated`. El manager se apagó al terminar porque la RAM libre de Windows bajó a aproximadamente 1,6 GiB. Tampoco representa alta disponibilidad; hubo una interrupción intencional.

## RF-04: compatibilidad de Falco en este equipo

Docker Desktop utiliza WSL2 con kernel `6.18.33.2-microsoft-standard-WSL2`. Se comprobó que el kernel presenta `/sys/kernel/btf/vmlinux` y `/sys/kernel/tracing`. Esos requisitos parciales no prueban que Falco pueda observar los procesos y contenedores del portal. La [guía oficial de Falco para Docker](https://falco.org/docs/getting-started/falco-docker-quickstart/) declara que su procedimiento no funciona en Windows con Docker Desktop. Por ello, **Falco aún no está desplegado ni validado** en esta arquitectura.

Para mantener todo en el mismo equipo, la siguiente ruta a evaluar es un Linux virtualizado local con Falco y un workload de prueba en ese mismo kernel. Si se exige detección sobre el portal actual, el portal y Falco tendrían que ejecutarse en el mismo entorno Linux o demostrarse experimentalmente visibilidad entre entornos; una alerta en otro workload no prueba cobertura del portal. Antes de instalar esa ruta hay que reservar espacio y RAM: en esta fase C: tenía 40,47 GiB libres y Windows 2,88 GiB de RAM libre con portal/base encendidos y Wazuh detenido. La prueba de tres componentes Wazuh simultáneos sigue pendiente.

## Capturas para el informe

1. Abrir `docs/evidencias/disponibilidad-postgresql.json` en VS Code y capturar el bloque `http` con 503/200 y los tipos de `audit_events`. El archivo no contiene contraseñas ni datos académicos.
2. En PowerShell, desde la raíz del proyecto, ejecutar `docker compose ps -a` y capturar `uts-database` y `uts-portal` en estado `healthy`. Hacer esta captura después de la prueba.
3. Si se necesita una captura de las reglas Wazuh 100102/100103, repetir `wazuh-logtest` con el manager encendido y dejar visible `Phase 3`, identificador y `Alert to be generated`; rotularla **prueba sintética de reglas**, nunca detección en vivo. Mantener indexer y dashboard detenidos para esa operación.
4. Capturar la pantalla de Falco solo después de observar una alerta real atribuible al workload que se declara monitoreado. El chequeo BTF/tracefs es una evaluación técnica, no evidencia de detección.

## Fuentes

- [Falco: procedimiento Docker y limitación de Docker Desktop en Windows](https://falco.org/docs/getting-started/falco-docker-quickstart/).
- [Falco: despliegue como contenedor y controlador modern eBPF](https://falco.org/docs/setup/container/).
