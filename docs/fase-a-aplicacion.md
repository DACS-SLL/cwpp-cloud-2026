# Fase A: aplicación académica

## Alcance implementado

El portal consulta las tres tablas existentes de PostgreSQL. No se cambió el esquema, la contraseña de la base ni el volumen. Las cuentas son exclusivamente de demostración y se configuran fuera de la imagen.

| Rol | Cursos | Matrículas y notas | Lista de estudiantes |
| --- | --- | --- | --- |
| Estudiante | Todos los cursos | Solo las propias, asociadas al ID de estudiante de prueba | Denegada (HTTP 403) |
| Docente | Todos los cursos | Todas | Permitida |
| Administrador | Todos los cursos | Todas | Permitida |

La autorización se comprueba en el servidor antes de cada consulta. Ocultar enlaces en la interfaz solo mejora la navegación. Para el piloto, `estudiante_demo` corresponde al registro de estudiante con ID 1. No existe vinculación con identidades institucionales reales.

## Credenciales y sesión

`python scripts/provision_demo_users.py` crea tres contraseñas aleatorias, guarda únicamente sus hashes PBKDF2 con sal en la variable `PORTAL_USERS_B64` de `.env` y genera una clave aleatoria de firma de sesión. El archivo `credenciales_portal.txt` contiene las contraseñas iniciales para uso local y está excluido por `.gitignore`. No se rota una configuración existente de forma automática. La contraseña de PostgreSQL permanece igual.

Para ingresar, abrir `http://localhost:8080/login` y consultar **localmente** `credenciales_portal.txt`. Guardar las contraseñas en un lugar seguro y borrar ese archivo cuando ya no se necesite. La sesión caduca tras 30 minutos, usa cookie `HttpOnly` y `SameSite=Strict`, y el cierre de sesión requiere POST con token CSRF. El piloto usa HTTP local; antes de exponerlo a otros equipos se necesitarían HTTPS, cookies `Secure`, gestión institucional de identidades y controles adicionales como limitación de intentos.

## Eventos y monitoreo

Los eventos `auth_required`, `login_failed`, `login_success`, `access_denied`, `data_access` y `logout` salen como líneas JSON en los logs del contenedor. Incluyen hora UTC, ruta, usuario, rol, origen y, para consultas, recurso y número de filas. No registran contraseñas ni contenido académico. Revisar con `docker compose logs --tail=100 portal`. `/health` sigue público para monitoreo y verifica la conexión a PostgreSQL; devuelve HTTP 503 si falla. La persistencia, protección y centralización de logs quedan pendientes de la fase de seguridad de infraestructura.

No se creó un endpoint HTTP de auditoría: los eventos se obtienen desde Docker para evitar publicar los registros a través del portal. Los logs actuales satisfacen una demostración de RF-01 y dan visibilidad parcial para RF-05 y RF-06; todavía no equivalen a monitoreo directo del motor PostgreSQL ni a una plataforma CWPP.

## Verificación realizada

1. `docker compose config --quiet` y compilación sintáctica de Python: correctos.
2. `docker compose up -d --build --no-deps portal`: recreó solo el portal; PostgreSQL siguió `healthy` en el contenedor previo.
3. `python scripts/smoke_portal.py`: ingreso, permisos, consultas y salida correctos para los tres roles. Verificó 7 cursos, 20 estudiantes y 60 matrículas para los roles autorizados, y solo 3 matrículas para el estudiante de prueba.
4. Los logs mostraron un intento fallido, un acceso denegado y consultas autorizadas en formato JSON.

## Límites para la siguiente fase

La autenticación actual sirve para el entorno local y datos simulados. No hay usuarios almacenados en una tabla, recuperación de contraseñas, controles por docente o curso, retención de logs ni detección en runtime. Wazuh y Falco todavía no están instalados.
