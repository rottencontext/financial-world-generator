"""A local viewer for worlds/: pick a run from a dropdown and read its days, agents and records.

    uv run python ui/server.py              # http://127.0.0.1:8765
    uv run python ui/server.py --port 8080

Reads worlds/ on every request, so new runs and a run in progress show up on refresh.
"""

import argparse
import contextlib
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
WORLDS = ROOT / "worlds"
STATIC = Path(__file__).resolve().parent
PAGES = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
TYPES = {".html": "text/html", ".js": "text/javascript", ".css": "text/css"}
MAX_TEXT = 2_000_000
LIVE_SECONDS = 120


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(errors="replace"))
    except (OSError, ValueError):
        return None


def read_events(path: Path) -> list[dict[str, Any]]:
    events = []
    if path.exists():
        for line in path.read_text(errors="replace").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if isinstance(event, dict):
                events.append(event)
    return events


def run_dirs(worlds: Path) -> list[Path]:
    """Every folder under worlds/ that holds files directly is a run."""
    if not worlds.is_dir():
        return []
    return sorted(
        folder
        for folder in [worlds, *worlds.rglob("*")]
        if folder.is_dir()
        and folder != worlds
        and any(child.is_file() for child in folder.iterdir())
    )


def is_live(folder: Path) -> bool:
    log = folder / "log.jsonl"
    return (
        not (folder / "run.json").exists()
        and log.exists()
        and time.time() - log.stat().st_mtime < LIVE_SECONDS
    )


def list_worlds(worlds: Path = WORLDS) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for folder in run_dirs(worlds):
        rel = folder.relative_to(worlds)
        world, name = rel.parts[0], "/".join(rel.parts[1:]) or "(top)"
        summary = read_json(folder / "run.json") or {}
        modified = max(child.stat().st_mtime for child in folder.iterdir() if child.is_file())
        groups.setdefault(world, []).append(
            {
                "id": rel.as_posix(),
                "name": name,
                "status": summary.get("status") or ("running" if is_live(folder) else None),
                "cost_usd": summary.get("cost_usd"),
                "first_date": summary.get("first_date"),
                "last_date": summary.get("last_date"),
                "modified": modified,
            }
        )
    return [
        {"world": world, "runs": sorted(runs, key=lambda run: -run["modified"])}
        for world, runs in sorted(groups.items())
    ]


def resolve_run(run_id: str, worlds: Path = WORLDS) -> Path | None:
    folder = (worlds / run_id).resolve()
    if folder == worlds.resolve() or not folder.is_relative_to(worlds.resolve()):
        return None
    return folder if folder.is_dir() else None


def load_run(folder: Path, worlds: Path = WORLDS, root: Path = ROOT) -> dict[str, Any]:
    summary = read_json(folder / "run.json")
    prompt_text = None
    if summary and isinstance(summary.get("prompt"), str):
        prompt_path = (root / summary["prompt"]).resolve()
        if prompt_path.is_relative_to(root.resolve()) and prompt_path.is_file():
            prompt_text = prompt_path.read_text(errors="replace")[:MAX_TEXT]
    world_py = folder / "world.py"
    stderr = folder / "world_stderr.log"
    return {
        "id": folder.relative_to(worlds.resolve()).as_posix(),
        "live": is_live(folder),
        "run": summary,
        "prompts": read_json(folder / "prompts.json"),
        "records": read_json(folder / "records.json"),
        "memory": read_json(folder / "memory.json"),
        "events": read_events(folder / "log.jsonl"),
        "world_py": world_py.read_text(errors="replace")[:MAX_TEXT] if world_py.exists() else None,
        "stderr": stderr.read_text(errors="replace")[-MAX_TEXT:] if stderr.exists() else None,
        "prompt_text": prompt_text,
        "files": [
            {"name": child.name, "size": child.stat().st_size}
            for child in sorted(folder.iterdir())
            if child.is_file()
        ],
    }


def read_file(folder: Path, name: str) -> str | None:
    path = (folder / name).resolve()
    if path.parent != folder or not path.is_file():
        return None
    return path.read_text(errors="replace")[:MAX_TEXT]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        url = urlparse(self.path)
        query = {key: values[0] for key, values in parse_qs(url.query).items()}
        if url.path in PAGES:
            page = STATIC / PAGES[url.path]
            self.send(200, page.read_bytes(), TYPES[page.suffix])
        elif url.path == "/api/worlds":
            self.send_json(list_worlds())
        elif url.path in ("/api/run", "/api/file"):
            folder = resolve_run(query.get("id", ""))
            if folder is None:
                self.send(404, b"no such run", "text/plain")
            elif url.path == "/api/run":
                self.send_json(load_run(folder))
            else:
                text = read_file(folder, query.get("name", ""))
                if text is None:
                    self.send(404, b"no such file", "text/plain")
                else:
                    self.send(200, text.encode(), "text/plain")
        else:
            self.send(404, b"not found", "text/plain")

    def send_json(self, value: Any) -> None:
        self.send(200, json.dumps(value, default=str).encode(), "application/json")

    def send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8765)
    port = parser.parse_args().port
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Worlds viewer: http://127.0.0.1:{port}  (Ctrl-C to stop)", flush=True)
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()


if __name__ == "__main__":
    main()
