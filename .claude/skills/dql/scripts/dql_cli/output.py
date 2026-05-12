import json
import sys
from typing import Any


def emit_json(data: Any, pretty: bool = True) -> None:
    sys.stdout.write(json.dumps(data, indent=2 if pretty else None, ensure_ascii=False))
    sys.stdout.write("\n")


def emit_lines(lines: list) -> None:
    for line in lines:
        sys.stdout.write(f"{line}\n")
