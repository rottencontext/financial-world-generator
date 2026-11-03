"""log.jsonl: one JSON line per event, written as it happens, plus the running model cost."""

import json
import threading
from pathlib import Path
from typing import Any


class RunLog:
    def __init__(self, path: Path):
        self._file = path.open("a")
        self._lock = threading.Lock()
        self.cost_usd = 0.0

    def write(self, event: dict[str, Any]) -> None:
        with self._lock:
            self._file.write(json.dumps(event, default=str) + "\n")
            self._file.flush()

    def cost(self, usage: dict[str, Any]) -> None:
        with self._lock:
            self.cost_usd += float(usage.get("cost") or 0)

    def close(self) -> None:
        self._file.close()
