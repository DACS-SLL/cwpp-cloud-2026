# Diagnóstico y puesta en marcha del portal UTS

## Hallazgo

El archivo real es `compose.yml`, no `compose.yaml`. Antes de la corrección solo definía `database`; por eso `docker compose config --quiet` era válido y `docker compose ps -a` mostraba únicamente `uts-database`. No existían un contenedor ni logs de `portal`. Además, `app.py`, `requirements.txt` y ambas plantillas estaban vacíos. El Dockerfile previsto también estaba vacío y ubicado bajo `templates/`, fuera del contexto de construcción esperado.

PostgreSQL estaba `healthy` y sus logs indicaban que aceptaba conexiones. La causa comprobada de la falta de respuesta en `localhost:8080` era la ausencia del servicio de aplicación, su implementación y la publicación del puerto. No se atribuyó el fallo original a `internal: true`.

## Corrección

- `portal` se construye desde `app/backend`, ejecuta Flask con Gunicorn y publica `127.0.0.1:8080:8080`.
- La base permanece únicamente en `uts_internal` (`internal: true`). El portal pertenece a esa red para consultar `database` y a `portal_access` para recibir solicitudes publicadas desde Windows.
- La contraseña se lee de `.env` mediante Compose; no se copia a la imagen ni se documenta aquí.
- `/health` ejecuta una consulta `SELECT 1` y devuelve HTTP 503 si la base no responde.
- Las vistas consultan las tablas existentes sin modificar registros.

## Verificación realizada

1. `docker compose config --quiet`: correcto.
2. `docker compose up -d --build --no-deps portal`: construyó y arrancó solo el portal; no recreó PostgreSQL ni su volumen.
3. `docker compose ps -a`: `uts-database` saludable y `uts-portal` activo, con `127.0.0.1:8080->8080/tcp`.
4. Logs de Gunicorn: proceso principal y dos workers iniciados.
5. DNS desde `portal`: `database` resuelve a una IP de la red interna. Flask, psycopg y Gunicorn están instalados.
6. Solicitudes desde Windows: `/`, `/health`, `/estudiantes`, `/cursos` y `/matriculas` devolvieron HTTP 200. Las vistas mostraron 20 estudiantes, 7 cursos y 60 matrículas.

## Operación

Desde la carpeta del proyecto: `docker compose up -d --build portal`. Abrir `http://localhost:8080`. Para inspeccionar: `docker compose ps -a` y `docker compose logs --tail=100 portal`.

Esta etapa inicial fue un piloto de consulta con datos simulados. La fase de autenticación y roles se documenta en `docs/fase-a-aplicacion.md`. Los componentes CWPP aún no están incorporados; el acceso del host se limita a `127.0.0.1`.
