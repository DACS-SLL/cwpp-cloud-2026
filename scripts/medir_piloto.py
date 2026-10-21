"""Mide latencia local del piloto sin imprimir datos ni credenciales."""

from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics
import time

from smoke_portal import BASE, client, csrf, fetch


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "evidencias" / "metricas-base.json"
SAMPLES = 30


def admin_password():
    for line in (ROOT / "credenciales_portal.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("admin_demo="):
            return line.split("=", 1)[1]
    raise RuntimeError("Falta la cuenta admin_demo local")


def measure(opener, path):
    values = []
    errors = 0
    for _ in range(SAMPLES):
        start = time.perf_counter()
        status, url, _ = fetch(opener, path)
        values.append((time.perf_counter() - start) * 1000)
        if status != 200 or url != BASE + path:
            errors += 1
    ordered = sorted(values)
    return {
        "samples": SAMPLES,
        "http_errors": errors,
        "median_ms": round(statistics.median(ordered), 2),
        "p95_ms": round(ordered[math.ceil(0.95 * SAMPLES) - 1], 2),
        "max_ms": round(ordered[-1], 2),
    }


def main():
    opener = client()
    _, _, page = fetch(opener, "/login")
    status, url, _ = fetch(opener, "/login", {
        "csrf": csrf(page), "username": "admin_demo", "password": admin_password(),
    })
    if status != 200 or url != BASE + "/":
        raise RuntimeError("No se pudo iniciar la sesión de prueba")

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Linea base local sin Wazuh ni Falco; solicitudes secuenciales",
        "routes": {path: measure(opener, path) for path in ("/health", "/cursos", "/matriculas")},
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for path, result in report["routes"].items():
        print(f"{path}: {result['samples']} solicitudes, errores={result['http_errors']}, mediana={result['median_ms']} ms, p95={result['p95_ms']} ms")
    print("Resultados guardados sin contraseñas ni contenido académico.")


if __name__ == "__main__":
    main()
