# Fase D: prueba controlada de Wazuh

**Estado al 21 de octubre de 2026:** Wazuh 4.14.9 se probó en dos sesiones controladas. Indexer y manager generaron dos alertas reales; después, indexer y dashboard permitieron ingresar con la cuenta `admin`. Los tres componentes están detenidos por falta de RAM física. El portal y PostgreSQL siguen saludables. Los volúmenes y las alertas permanecen guardados.

## Comprobaciones realizadas

1. Se estableció `%UserProfile%\.wslconfig` con `memory=9GB`. Docker reconoció 9 371 779 072 bytes utilizables (aproximadamente 8,73 GiB). `vm.max_map_count` respondió `262144`.
2. Se generaron los certificados TLS locales del stack de un nodo. Se descargaron las imágenes oficiales de indexer, manager y dashboard 4.14.9.
3. Se crearon contraseñas aleatorias locales para `admin`, `kibanaserver` y la API. Están en `.env` y configuraciones locales excluidas de Git; no deben mostrarse en capturas. El indexer respondió HTTP 200 con la contraseña propia y 401 sin autenticación.
4. El manager leyó el volumen persistente de auditoría del portal. `wazuh-logtest` emparejó un evento sintético `login_failed` con la regla `100100`, nivel 7.
5. Se ejecutó `scripts/smoke_portal.py` con el manager encendido. El archivo persistente `alerts.json` registró **una alerta real `login_failed` (regla 100100) y una `access_denied` (regla 100101)**. El resumen sin usuario, IP ni contenido académico está en `docs/evidencias/wazuh-alertas-verificadas.json`.
6. En una segunda sesión se inició el dashboard con el indexer, mientras el manager permaneció detenido. `https://localhost:8443/app/login` respondió HTTP 200. El usuario confirmó el ingreso y aportó `docs/evidencias/capturas/15-dashboard-api-offline.png`, donde la conexión a `wazuh.manager` figura `Offline`.

La prueba muestra detección e ingesta de esos dos eventos y acceso al dashboard. No demuestra visualización de las alertas dentro del dashboard, cobertura Falco ni alertas de disponibilidad o fallo de consultas: las reglas 100102 y 100103 no recibieron eventos de prueba.

## Límite de recursos y decisión de operación

Con indexer y manager encendidos, Windows llegó a **0,12 GiB de RAM física libre**. Se detuvieron ambos con `docker compose stop`, sin eliminar volúmenes. Después, la memoria libre volvió a superar 3 GiB y más tarde llegó a 6,01 GiB. En la prueba separada del dashboard, indexer y dashboard redujeron la RAM libre a menos de 1 GiB; se detuvieron tras recibir la captura. Se desactivó el reinicio automático de los contenedores Wazuh y del Compose del stack, por lo que un reinicio de Docker no debería encenderlos de nuevo.

C: quedó cerca de 40,5 GiB libres tras las descargas, por debajo de la recomendación de 50 GB de almacenamiento para imágenes y datos del stack de un nodo. La cifra es una guía de capacidad, no el tamaño de descarga de Wazuh. No se usó D:.

Para completar el dashboard y medir rendimiento con el stack íntegro se necesita más memoria física disponible y espacio suficiente en C: (o mover el almacenamiento Docker a una unidad con capacidad real). Al reanudar, comprobar primero recursos y estado de volúmenes; no ejecutar `docker compose down -v`.

## Capturas que ya puedes tomar

- **Detección real:** abre `docs/evidencias/wazuh-alertas-verificadas.json` en VS Code. Captura `counts_by_rule` y los dos objetos `alerts`. El archivo no muestra credenciales ni datos académicos.
- **Ingreso al dashboard:** usa `docs/evidencias/capturas/15-dashboard-api-offline.png`. Etiquétala «Dashboard accesible; API del manager offline durante la prueba por límite de RAM». Si repites la captura, deja visible la URL sin mostrar credenciales.
- **Componentes instalados y detenidos:** en PowerShell, desde `security/wazuh/upstream/single-node`, ejecuta `docker compose ps -a` y `docker image ls | Select-String wazuh`. Captura nombres, versiones y estados. No presentes esa captura como stack operativo.
- **Registro listo para captura:** abre `docs/evidencias/wazuh-componentes.txt`; incluye las tres imágenes y las horas UTC en que indexer y manager estuvieron activos, sin secretos.
- **Portal conservado:** desde la raíz del proyecto, ejecuta `docker compose ps -a` y captura portal y base `healthy`.

La captura de las tres piezas activas, la visualización de alertas dentro del dashboard y el consumo conjunto quedan pendientes de un equipo con más margen de recursos.

## Referencias

- [Wazuh: requisitos y despliegue del stack Docker de un nodo](https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html).
- [Microsoft: configuración global y reinicio de WSL](https://learn.microsoft.com/en-us/windows/wsl/wsl-config).
