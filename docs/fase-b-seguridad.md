# Fase B: seguridad de infraestructura (estado real)

> Actualización del 21 de octubre de 2026: después de esta fase se confirmaron dos alertas reales de Wazuh y se ingresó al dashboard en una prueba separada. La visualización de alertas con los tres componentes activos sigue pendiente por falta de RAM. Ver `docs/fase-d-wazuh.md`.

## Implementado y comprobado

- **RF-02:** Docker Scout analizó la imagen local del portal. El informe actual está en `docs/evidencias/scout-portal-actual.md`; el previo al endurecimiento queda en `scout-portal-antes.md`. El resultado actual reporta un hallazgo alto en `zlib` y ninguno crítico. Es un hallazgo de escáner; la explotabilidad en este portal no se ha demostrado y el informe indica que no hay versión corregida en esa fuente.
- **RF-03:** el portal se ejecuta como UID/GID 10001, con sistema de archivos raíz de solo lectura, `cap_drop: ALL`, `no-new-privileges`, límite de 100 procesos, 256 MiB de memoria y `/tmp` temporal. `docker inspect` confirmó estas opciones. La base de datos conserva su configuración y volumen originales.
- **RF-06:** el `healthcheck` del portal comprueba HTTP y PostgreSQL. `docker compose ps -a` mostró portal y base saludables.
- **RNF-05:** `docker stats --no-stream` ofrece la línea base de CPU y RAM. El script `scripts/evidencia_infra.ps1` reúne salidas seguras para capturas.
- **Preparación de Wazuh:** el portal ahora guarda eventos JSON con rotación en el volumen `uts-cwpp_audit_logs`. Se verificaron 60 eventos acumulados de seis tipos tras recrear el portal y repetir la prueba de roles. El paquete oficial Wazuh 4.14.9 está preparado en `security/wazuh/upstream/single-node`: su manager montará el volumen en modo lectura y recogerá esos archivos como JSON. Hay cuatro reglas preparadas para accesos y fallos. La configuración Compose y el XML se validaron, pero **Wazuh no ha arrancado ni ingerido eventos**.

Las pruebas de ingreso y consultas de `scripts/smoke_portal.py` volvieron a pasar después del endurecimiento.

## Wazuh: requisito de recursos antes del despliegue

El stack oficial de un nodo requiere **al menos 8 GB para el host Docker, 4 CPU y 50 GB de capacidad de almacenamiento**. Los 50 GB son una referencia de capacidad para imágenes y datos; no significa una descarga inmediata de 50 GB. Docker expuso 8 CPU pero solo **6,68 GiB** y Windows reportó alrededor de **0,4 GiB libres** en la última comprobación. Su disco virtual reside en C:, no en D:. Por ello el manager, indexer y dashboard no se han arrancado. Para continuar habrá que liberar memoria y elevar el límite de WSL/Docker, lo que requiere reiniciar Docker Desktop. La preparación y los pasos pendientes están en `security/wazuh/README.md`.

## Falco: alcance pendiente

Falco necesita observar eventos del kernel Linux que ejecuta los workloads. En este equipo solo aparece la distribución WSL `docker-desktop`; no se ha comprobado que una instalación en otra distribución WSL observe estos contenedores. Una VM Linux independiente solo permitirá demostrar detección sobre workloads que se ejecuten **en esa misma VM**. Falco no está instalado ni se atribuye cobertura a este piloto todavía.

## Evidencia y siguientes comprobaciones

La guía `docs/capturas-evidencia.md` indica las capturas que se pueden tomar ahora y las posteriores para Wazuh/Falco. Antes de integrar el SIEM se debe medir memoria libre de nuevo, documentar el ajuste de Docker/WSL y comprobar que la base sigue saludable. No usar `docker compose down -v`: eliminaría volúmenes.

## Fuentes técnicas

- [Wazuh: despliegue Docker y requisitos del stack de un nodo](https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html).
- [Wazuh: integración del Docker listener](https://documentation.wazuh.com/current/user-manual/capabilities/container-security/monitoring-docker.html).
- [Falco: instalación en contenedor y drivers](https://falco.org/docs/setup/container/).
