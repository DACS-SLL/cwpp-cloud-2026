# cwpp-cloud-2026

Piloto CWPP local para un portal académico de demostración: Flask/Gunicorn, PostgreSQL, registros de auditoría, pruebas controladas de Wazuh y detección de Falco en Ubuntu. El caso institucional y sus datos son ficticios.

## Empezar por aquí

| Si necesitas... | Lee... |
| --- | --- |
| Integrar este aporte al informe del grupo | [Informe editable del integrante 2](docs/entregables/informe-integrante-2.docx) y [fuente Markdown](docs/informe-integrante-2.md) |
| Reproducirlo en otra VM | [Guía de reproducción](docs/guia-reproduccion.md) |
| Seleccionar y explicar capturas | [Guía de análisis de evidencias](docs/guia-analisis-evidencias.md) |
| Ver el mapa de carpetas y documentos | [Índice de docs](docs/README.md) |
| Entender las topologías | [Arquitectura Windows y Ubuntu](docs/arquitectura-actual.md) |

Para recrear el DOCX tras editar su fuente, usa el Python del entorno de documentos con `python scripts/generar_informe_integrante_2.py` y revisa el resultado en Word. El directorio `docs/evidencias/capturas/` y las credenciales son locales y no se publican en Git.

En un **clon Git** usa siempre `-f ubuntu.compose.yaml` como configuración base de Ubuntu. El ZIP generado contiene esa misma configuración con el nombre `compose.yaml` en su raíz. `compose.yml` en la raíz conserva el piloto histórico de Windows; elegir `-f` evita ambigüedades.

## Ejecutar el portal en Ubuntu

El portal se construye ahora desde `app/backend` del mismo commit y se etiqueta `uts-cwpp-portal:local` en Ubuntu; `d4c5g/uts-cwpp-portal:2026-10-21` es la imagen usada en las pruebas históricas. El paquete de despliegue se genera con `python scripts/paquetizar_ubuntu.py` y queda en `dist/`. Lee [deploy/ubuntu/README.md](deploy/ubuntu/README.md) para instalar Docker Engine dentro de la VM, crear contraseñas locales y arrancar el portal y Falco con Compose. PostgreSQL usa `postgres:17-alpine`. El SQL versionado contiene solo datos de demostración.

## Estado verificado

- Portal y PostgreSQL saludables; cuentas de tres roles, 20 estudiantes de prueba, 7 cursos y 60 matrículas comprobados.
- Auditoría JSON persistente y detección real por Wazuh de `login_failed` (100100) y `access_denied` (100101).
- Caída controlada de PostgreSQL: HTTP 503 durante la interrupción, HTTP 200 tras recuperar el servicio. Reglas Wazuh 100102/100103 verificadas con eventos sintéticos.
- Dashboard Wazuh accesible en una sesión separada; el manager figuró desconectado en esa sesión por límite de RAM.
- En Ubuntu VirtualBox, el portal y PostgreSQL quedaron saludables y pasó la prueba de los tres roles. Falco 0.45.0 generó dos alertas reales al abrir una shell en el contenedor `uts-portal`.
- Falco también quedó administrado por Compose en Ubuntu; una alerta nueva de `prueba-falco-compose` confirmó la detección después del cambio y se registró una muestra puntual de recursos.
- Falco escribe JSON y Wazuh manager 4.14.9 lo procesa en la VM: una alerta real 100200 para `prueba-falco-wazuh` quedó registrada en `alerts.json`; el portal continuó saludable.
- El mismo Wazuh manager de Ubuntu leyó la auditoría persistente del portal y generó alertas reales 100100 (`login_failed`) y 100101 (`access_denied`) tras una nueva prueba de roles.

Lee [docs/fase-d-wazuh.md](docs/fase-d-wazuh.md), [docs/fase-e-disponibilidad.md](docs/fase-e-disponibilidad.md), [docs/fase-f-falco-ubuntu.md](docs/fase-f-falco-ubuntu.md) y [docs/fase-g-falco-compose.md](docs/fase-g-falco-compose.md) para conocer el alcance y las limitaciones. Las capturas originales permanecen solo en el equipo local; el repositorio incluye evidencias textuales depuradas.

La [fase H](docs/fase-h-preparacion-wazuh-falco.md) documenta la prueba acotada Falco → Wazuh manager en Ubuntu y su alerta en vivo. Este despliegue no incluye indexer ni dashboard.

Los [dos diagramas actuales](docs/arquitectura-actual.md) distinguen la PC Windows y la VM Ubuntu. La [fase I](docs/fase-i-auditoria-wazuh-ubuntu.md) documenta la lectura de auditoría y las alertas nuevas en el manager de Ubuntu. Las [extensiones a VMs, Kubernetes y serverless](docs/extensiones-arquitectura.md) se describen como diseño futuro, sin atribuirles un despliegue.

La [entrega técnica del integrante 2](docs/entrega-integrante-2.md) reúne arquitectura, componentes y límites. El informe editable para el integrante 4 está en `docs/entregables/` y las guías de reproducción y lectura de imágenes están en `docs/`.

## Wazuh

La copia oficial de Wazuh es un repositorio independiente y no se versiona aquí. Ejecuta `powershell -ExecutionPolicy Bypass -File scripts/preparar_wazuh_upstream.ps1` para obtener la etiqueta oficial `v4.14.9` y aplicar los archivos adaptados del directorio `security/wazuh/overrides/`. Los certificados, contraseñas y volúmenes se crean localmente y no se publican. [security/wazuh/README.md](security/wazuh/README.md) explica las pruebas realizadas.

## Archivos privados

`.env`, `credenciales_portal.txt`, certificados, configuraciones locales con hashes, capturas y el ZIP generado están excluidos de Git. No uses `docker compose down -v`: borraría los datos persistentes del piloto.
