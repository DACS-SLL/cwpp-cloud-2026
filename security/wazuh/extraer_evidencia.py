"""Extrae evidencia mínima de alertas Wazuh del volumen persistente.

No requiere encender Wazuh y omite usuario, IP, mensaje original y datos del portal.
"""

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs" / "evidencias" / "wazuh-alertas-verificadas.json"
RULES = {"100100", "100101", "100102", "100103"}


def main():
    result = subprocess.run(
        ["docker", "run", "--rm", "-v", "single-node_wazuh_logs:/logs:ro",
         "alpine:3.20", "cat", "/logs/alerts/alerts.json"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    )
    records = []
    for line in result.stdout.splitlines():
        entry = json.loads(line)
        rule = entry.get("rule", {})
        rule_id = str(rule.get("id", ""))
        if rule_id not in RULES:
            continue
        records.append({
            "timestamp": entry.get("timestamp"),
            "rule_id": rule_id,
            "level": rule.get("level"),
            "description": rule.get("description"),
            "event": entry.get("data", {}).get("event"),
        })
    report = {
        "extracted_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Volumen Docker single-node_wazuh_logs, archivo alerts.json",
        "scope": "Alertas reales de auditoría del portal; no incluye dashboard ni Falco",
        "counts_by_rule": dict(sorted(Counter(r["rule_id"] for r in records).items())),
        "alerts": records,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Alertas verificadas:", report["counts_by_rule"])
    print("Evidencia sanitizada guardada en docs/evidencias/wazuh-alertas-verificadas.json")


if __name__ == "__main__":
    main()
