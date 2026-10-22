"""Genera eventos de auditoría y comprueba alertas nuevas en Wazuh Ubuntu."""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
CONTAINER = "uts-wazuh-manager"
ALERTS = "/var/ossec/logs/alerts/alerts.json"
EXPECTED = {"100100": "login_failed", "100101": "access_denied"}


def alert_time(value: str) -> datetime | None:
    for pattern in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(value, pattern)
        except ValueError:
            pass
    return None


def recent_alerts(started: datetime) -> dict[str, dict]:
    result = subprocess.run(
        ["docker", "exec", CONTAINER, "cat", ALERTS],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        return {}
    found = {}
    for line in result.stdout.splitlines():
        try:
            alert = json.loads(line)
        except json.JSONDecodeError:
            continue
        rule_id = str(alert.get("rule", {}).get("id", ""))
        timestamp = alert_time(alert.get("timestamp", ""))
        if rule_id in EXPECTED and timestamp is not None and timestamp >= started:
            found[rule_id] = alert
    return found


def main() -> int:
    started = datetime.now(timezone.utc)
    smoke = subprocess.run(
        [sys.executable, str(ROOT / "scripts/smoke_portal.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if smoke.returncode:
        print("Falló la prueba funcional del portal; revisa su salida local.", file=sys.stderr)
        print(smoke.stdout[-1000:], file=sys.stderr)
        print(smoke.stderr[-1000:], file=sys.stderr)
        return 1

    for _ in range(15):
        alerts = recent_alerts(started)
        if EXPECTED.keys() <= alerts.keys():
            print("Portal: ingreso, permisos y consultas correctos")
            for rule_id, event in EXPECTED.items():
                alert = alerts[rule_id]
                print(f"Wazuh: regla {rule_id}, nivel {alert['rule']['level']}, evento {event}")
                print(f"Hora UTC: {alert['timestamp']}")
            print(f"Archivo de alertas: {ALERTS}")
            return 0
        time.sleep(2)
    missing = ", ".join(sorted(EXPECTED.keys() - alerts.keys()))
    print(f"No aparecieron las alertas nuevas de Wazuh: {missing}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
