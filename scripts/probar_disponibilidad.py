"""Prueba controlada de caída de PostgreSQL, con recuperación en finally.

Ejecutar desde la raíz del proyecto: python scripts/probar_disponibilidad.py
Solo usa las cuentas de demostración y no imprime credenciales ni datos académicos.
"""

from datetime import datetime, timezone
from http.cookiejar import CookieJar
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8080"
EVIDENCE = ROOT / "docs/evidencias/disponibilidad-postgresql.json"


def docker(*args):
    result = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=45)
    if result.returncode:
        raise RuntimeError(f"docker {' '.join(args[:2])} falló: {result.stderr.strip()[:300]}")
    return result.stdout.strip()


def fetch(opener, path, data=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    request = urllib.request.Request(BASE + path, data=body)
    try:
        with opener.open(request, timeout=12) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def wait_status(opener, path, expected, timeout=45):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            last = fetch(opener, path)
        except (urllib.error.URLError, TimeoutError):
            last = "unreachable"
        if last == expected:
            return last
        time.sleep(2)
    raise RuntimeError(f"{path}: esperaba HTTP {expected}; último resultado: {last}")


def main():
    db = docker("inspect", "--format", "{{.State.Running}}", "uts-database")
    portal = docker("inspect", "--format", "{{.State.Running}}", "uts-portal")
    if db != "true" or portal != "true":
        raise RuntimeError("Portal y base deben estar encendidos antes de comenzar")

    password = None
    for line in (ROOT / "credenciales_portal.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("admin_demo="):
            password = line.split("=", 1)[1]
    if not password:
        raise RuntimeError("Falta admin_demo en credenciales_portal.txt")

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    wait_status(opener, "/health", 200)
    with opener.open(BASE + "/login", timeout=12) as response:
        login_page = response.read().decode("utf-8")
    match = re.search(r'name="csrf" value="([^"]+)"', login_page)
    if not match:
        raise RuntimeError("Falta token CSRF de prueba")
    if fetch(opener, "/login", {"csrf": match.group(1), "username": "admin_demo", "password": password}) != 200:
        raise RuntimeError("No se pudo iniciar sesión de demostración")
    password = None
    wait_status(opener, "/cursos", 200)

    start = datetime.now(timezone.utc)
    stopped = False
    try:
        docker("stop", "uts-database")
        stopped = True
        health_down = wait_status(opener, "/health", 503)
        query_down = wait_status(opener, "/cursos", 503)
    finally:
        if stopped:
            docker("start", "uts-database")

    health_up = wait_status(opener, "/health", 200, timeout=90)
    query_up = wait_status(opener, "/cursos", 200, timeout=45)
    end = datetime.now(timezone.utc)

    # Extraer solo tipos y tiempos; nunca usuarios, IP, filas ni credenciales.
    audit = docker("exec", "uts-portal", "python", "-c",
                   "from pathlib import Path; print(Path('/var/log/uts/audit.jsonl').read_text())")
    types = {"service_unavailable", "database_query_failed"}
    events = []
    for line in audit.splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("event") in types and entry.get("timestamp", "") >= start.isoformat():
            events.append({"timestamp": entry["timestamp"], "event": entry["event"]})
    found = {entry["event"] for entry in events}
    if found != types:
        raise RuntimeError(f"Faltan eventos de auditoría: {sorted(types - found)}")

    evidence = {
        "scope": "Prueba controlada local: portal y PostgreSQL en Docker Desktop; Wazuh/Falco apagados",
        "started_utc": start.isoformat(),
        "finished_utc": end.isoformat(),
        "http": {"health_during_outage": health_down, "query_during_outage": query_down,
                 "health_after_recovery": health_up, "query_after_recovery": query_up},
        "audit_events": events,
        "database_restarted": True,
    }
    EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prueba completada: 503 durante la caída, 200 después; {len(events)} eventos pertinentes.")
    print(f"Evidencia: {EVIDENCE}")


if __name__ == "__main__":
    main()
