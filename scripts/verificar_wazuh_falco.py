"""Comprueba una alerta Wazuh real de la prueba controlada de Falco."""

import json
import subprocess
import sys
import time


CONTAINER = "uts-wazuh-manager"
ALERTS = "/var/ossec/logs/alerts/alerts.json"
RULE_ID = "100200"
MARKER = "prueba-falco-wazuh"


def find_alert() -> dict | None:
    result = subprocess.run(
        ["docker", "exec", CONTAINER, "cat", ALERTS],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        return None
    for line in reversed(result.stdout.splitlines()):
        try:
            alert = json.loads(line)
        except json.JSONDecodeError:
            continue
        if str(alert.get("rule", {}).get("id")) == RULE_ID and MARKER in alert.get("full_log", ""):
            return alert
    return None


def main() -> int:
    for _ in range(15):
        alert = find_alert()
        if alert is not None:
            rule = alert["rule"]
            print(f"Hora Wazuh: {alert.get('timestamp', 'sin hora')}")
            print(f"Regla Wazuh: {rule['id']} (nivel {rule.get('level', 'sin nivel')})")
            print(f"Descripción: {rule.get('description', 'sin descripción')}")
            print("Origen: Falco, contenedor uts-portal")
            print(f"Marcador: {MARKER}")
            print(f"Archivo de alertas: {ALERTS}")
            return 0
        time.sleep(2)
    print("No apareció la alerta Wazuh 100200 para prueba-falco-wazuh.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
