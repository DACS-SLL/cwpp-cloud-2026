# cwpp-cloud-2026

Piloto CWPP local para un portal académico de demostración: Flask/Gunicorn, PostgreSQL, registros de auditoría, pruebas controladas de Wazuh y detección de Falco en Ubuntu.

## Ejecutar el portal en Ubuntu

La imagen `d4c5g/uts-cwpp-portal:2026-10-21` está publicada en Docker Hub. El paquete de despliegue se genera con `python scripts/paquetizar_ubuntu.py` y queda en `dist/`. Lee [deploy/ubuntu/README.md](deploy/ubuntu/README.md) para instalar Docker Engine dentro de la VM, crear contraseñas locales y arrancar el portal y Falco con Compose. PostgreSQL usa la imagen oficial `postgres:17-alpine`. El SQL versionado contiene solo identificadores y correos de demostración.

## Estado verificado

- Portal y PostgreSQL saludables; cuentas de tres roles, 20 estudiantes de prueba, 7 cursos y 60 matrículas comprobados.
- Auditoría JSON persistente y detección real por Wazuh de `login_failed` (100100) y `access_denied` (100101).
- Caída controlada de PostgreSQL: HTTP 503 durante la interrupción, HTTP 200 tras recuperar el servicio. Reglas Wazuh 100102/100103 verificadas con eventos sintéticos.
- Dashboard Wazuh accesible en una sesión separada; el manager figuró desconectado en esa sesión por límite de RAM.
- En Ubuntu VirtualBox, el portal y PostgreSQL quedaron saludables y pasó la prueba de los tres roles. Falco 0.45.0 generó dos alertas reales al abrir una shell en el contenedor `uts-portal`.
- Falco también quedó administrado por Compose en Ubuntu; una alerta nueva de `prueba-falco-compose` confirmó la detección después del cambio y se registró una muestra puntual de recursos.
- Falco escribe JSON y Wazuh manager 4.14.9 lo procesa en la VM: una alerta real 100200 para `prueba-falco-wazuh` quedó registrada en `alerts.json`; el portal continuó saludable.

Lee [docs/fase-d-wazuh.md](docs/fase-d-wazuh.md), [docs/fase-e-disponibilidad.md](docs/fase-e-disponibilidad.md), [docs/fase-f-falco-ubuntu.md](docs/fase-f-falco-ubuntu.md) y [docs/fase-g-falco-compose.md](docs/fase-g-falco-compose.md) para conocer el alcance y las limitaciones. Las capturas originales permanecen solo en el equipo local; el repositorio incluye evidencias textuales depuradas.

La [fase H](docs/fase-h-preparacion-wazuh-falco.md) documenta la prueba acotada Falco → Wazuh manager en Ubuntu y su alerta en vivo. Este despliegue no incluye indexer ni dashboard.

Los [dos diagramas actuales](docs/arquitectura-actual.md) distinguen la PC Windows y la VM Ubuntu. La [fase I](docs/fase-i-auditoria-wazuh-ubuntu.md) prepara la lectura de la auditoría del portal por el mismo manager de Ubuntu; requiere validación en vivo antes de atribuirle alertas nuevas.

## Wazuh

La copia oficial de Wazuh es un repositorio independiente y no se versiona aquí. Ejecuta `powershell -ExecutionPolicy Bypass -File scripts/preparar_wazuh_upstream.ps1` para obtener la etiqueta oficial `v4.14.9` y aplicar los archivos adaptados del directorio `security/wazuh/overrides/`. Los certificados, contraseñas y volúmenes se crean localmente y no se publican. [security/wazuh/README.md](security/wazuh/README.md) explica las pruebas realizadas.

## Archivos privados

`.env`, `credenciales_portal.txt`, certificados, configuraciones locales con hashes, capturas y el ZIP generado están excluidos de Git. No uses `docker compose down -v`: borraría los datos persistentes del piloto.
