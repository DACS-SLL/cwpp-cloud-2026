"""Muestra un evento de prueba Falco en JSON sin imprimir el log completo."""

import json
import sys
from pathlib import Path


LOG = Path("falco-logs/events.jsonl")
MARKER = "prueba-falco-json"


def main() -> int:
    if not LOG.is_file():
        print(f"No existe {LOG}; comprueba la configuración de file_output de Falco.", file=sys.stderr)
        return 1

    found = None
    with LOG.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                print(f"JSON inválido en la línea {number}: {error}", file=sys.stderr)
                return 1
            output = event.get("output", "")
            if (
                event.get("rule") == "Terminal shell in container"
                and MARKER in output
                and "container_name=uts-portal" in output
            ):
                found = event

    if found is None:
        print("No se encontró una alerta JSON de prueba-falco-json atribuida a uts-portal.", file=sys.stderr)
        return 1

    print(f"Hora UTC: {found.get('time', 'sin hora')}")
    print(f"Regla: {found['rule']}")
    print(f"Prioridad: {found.get('priority', 'sin prioridad')}")
    print("Contenedor: uts-portal")
    print(f"Marcador: {MARKER}")
    print(f"Archivo JSON: {LOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
