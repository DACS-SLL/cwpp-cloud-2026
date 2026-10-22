# Entrega técnica del integrante 2 · arquitectura e implementación

El [informe editable para el integrante 4](entregables/informe-integrante-2.docx) sigue la estructura de `Examen Parcial.pdf`. Su [fuente Markdown](informe-integrante-2.md), la [guía de reproducción](guia-reproduccion.md) y la [guía de análisis de imágenes](guia-analisis-evidencias.md) reúnen el material de traspaso.

## Alcance entregado

| Responsabilidad | Implementación y evidencia |
| --- | --- |
| Arquitectura lógica y física | [Dos diagramas separados](arquitectura-actual.md): PC Windows con pruebas iniciales y VM Ubuntu con el piloto integrado. SVG editables y PNG para el informe. |
| Infraestructura reproducible | [Compose raíz para clon Git](../ubuntu.compose.yaml), [Falco](../deploy/ubuntu/falco.compose.yaml) y [Wazuh manager](../deploy/ubuntu/wazuh-manager.compose.yaml); [guía de reproducción](guia-reproduccion.md) y ZIP local generado con `scripts/paquetizar_ubuntu.py`. |
| Portal y base de datos | Flask/Gunicorn y PostgreSQL 17 en contenedores separados; volumen de datos persistente; cuentas y registros ficticios; prueba de tres roles y endpoints de salud. |
| Seguridad de los contenedores | Portal con UID 10001, raíz de solo lectura, `cap_drop: ALL`, `no-new-privileges` y límites. Falco necesita privilegios y acceso al kernel de la misma VM; esas restricciones no se atribuyen a Falco. |
| Recolección de eventos | Portal escribe auditoría JSON en `audit_logs`; Falco escribe JSON en `falco-logs/events.jsonl`. El manager de Ubuntu monta ambos en solo lectura y conserva `alerts.json` en volumen. |
| Verificación de integración | [Falco → Wazuh](fase-h-preparacion-wazuh-falco.md): alerta real 100200. [Portal → Wazuh](fase-i-auditoria-wazuh-ubuntu.md): alertas reales 100100 y 100101. Portal y PostgreSQL permanecieron saludables. |
| Extensiones | [Diseño de ampliación](extensiones-arquitectura.md) a más VM, Kubernetes y funciones serverless, con sus límites de visibilidad. |

## Evidencias para el integrante 3

Las capturas locales `24` a `29` están en `docs/evidencias/capturas/` y se excluyen de Git. En el repositorio se incluyen resúmenes depurados [Falco → Wazuh](evidencias/wazuh-falco-ubuntu-verificacion.json) y [auditoría → Wazuh](evidencias/wazuh-portal-ubuntu-verificacion.json). Para trazabilidad del portal y la base también están [la caída controlada](evidencias/disponibilidad-postgresql.json), [las alertas iniciales de Windows](evidencias/wazuh-alertas-verificadas.json) y [el análisis de vulnerabilidades](evidencias/scout-portal-actual.md). Las capturas no contienen contraseñas ni datos académicos reales.

## Decisiones y límites que deben explicarse

1. **VM Linux para Falco:** observa los contenedores del mismo kernel Ubuntu. No se afirma cobertura de Falco sobre Docker Desktop de Windows.
2. **Wazuh manager sin indexer ni dashboard en Ubuntu:** el hardware del piloto no da margen suficiente para mantener el stack oficial completo junto a las demás cargas. Se verificaron alertas en `alerts.json`; no se afirma visualización en dashboard.
3. **Dos orígenes de eventos distintos:** la auditoría del portal demuestra intentos de acceso y denegaciones; Falco demuestra ejecución de shell en runtime. Las reglas 100102 y 100103 están preparadas, pero en Ubuntu no se atribuyen alertas de disponibilidad en vivo.
4. **Base de datos:** `data_access` describe consultas realizadas por el portal, no auditoría interna del motor PostgreSQL. La recuperación ante una interrupción se probó en un escenario controlado de Windows.
5. **Operación del laboratorio:** vigilar el tamaño de `falco-logs/events.jsonl`, memoria y disco; el log de Falco no rota automáticamente. Detener servicios con `docker compose stop` y conservar volúmenes. No publicar `.env`, credenciales, certificados ni logs completos.

## Reproducción y traspaso

El repositorio está en `https://github.com/DACS-SLL/cwpp-cloud-2026`. Para una VM nueva, seguir la [guía de Ubuntu](../deploy/ubuntu/README.md), generar credenciales localmente y usar los tres archivos Compose. Las pruebas controladas se ejecutan con `scripts/smoke_portal.py`, `scripts/verificar_falco_json.py`, `scripts/verificar_wazuh_falco.py` y `scripts/verificar_wazuh_portal_ubuntu.py`. Cada prueba produce salida breve, adecuada para capturas; los archivos de credenciales y registros sin depurar permanecen locales.
