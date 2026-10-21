"""Prueba de integración local de sesiones, roles y consultas del portal."""

from http.cookiejar import CookieJar
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8080"


def client():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))


def fetch(opener, path, data=None):
    request = urllib.request.Request(BASE + path, data=urllib.parse.urlencode(data).encode() if data else None)
    try:
        with opener.open(request, timeout=10) as response:
            return response.status, response.url, response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.code, error.url, error.read().decode("utf-8")


def csrf(html):
    match = re.search(r'name="csrf" value="([^"]+)"', html)
    assert match, "Falta el token CSRF"
    return match.group(1)


def count(html):
    match = re.search(r'<p>(\d+) registros</p>', html)
    assert match, "Falta el recuento"
    return int(match.group(1))


def main():
    credentials = {}
    for line in (ROOT / "credenciales_portal.txt").read_text(encoding="utf-8").splitlines():
        if "=" in line:
            username, password = line.split("=", 1)
            credentials[username] = password

    anonymous = client()
    assert fetch(anonymous, "/health")[0] == 200
    status, url, _ = fetch(anonymous, "/estudiantes")
    assert status == 200 and url.endswith("/login"), "La vista debe exigir ingreso"
    _, _, login_page = fetch(anonymous, "/login")
    status, _, body = fetch(anonymous, "/login", {"csrf": csrf(login_page), "username": "inexistente", "password": "incorrecta"})
    assert status == 200 and "Usuario o contraseña incorrectos" in body

    for username, expected in {
        "estudiante_demo": {"cursos": 7, "matriculas": 3, "estudiantes": 403},
        "docente_demo": {"cursos": 7, "matriculas": 60, "estudiantes": 20},
        "admin_demo": {"cursos": 7, "matriculas": 60, "estudiantes": 20},
    }.items():
        opener = client()
        _, _, page = fetch(opener, "/login")
        status, url, _ = fetch(opener, "/login", {"csrf": csrf(page), "username": username, "password": credentials[username]})
        assert status == 200 and url == BASE + "/", f"Falló el ingreso de {username}"
        for resource in ("cursos", "matriculas", "estudiantes"):
            status, _, body = fetch(opener, "/" + resource)
            if resource == "estudiantes" and username == "estudiante_demo":
                assert status == 403
            else:
                assert status == 200 and count(body) == expected[resource], (username, resource, status)
        _, _, home = fetch(opener, "/")
        status, _, _ = fetch(opener, "/logout", {"csrf": csrf(home)})
        assert status == 200
        assert fetch(opener, "/cursos")[1].endswith("/login")
        print(f"{username}: ingreso, permisos, consultas y salida correctos")
    print("Prueba de integración completada sin mostrar credenciales ni registros académicos.")


if __name__ == "__main__":
    main()
