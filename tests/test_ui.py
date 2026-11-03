"""The worlds viewer's server: run listing, run loading, and no reads outside worlds/."""

import importlib.util
import json
from pathlib import Path
from types import ModuleType

SERVER = Path(__file__).resolve().parent.parent / "ui" / "server.py"


def load_server() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ui_server", SERVER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_worlds(tmp_path: Path) -> Path:
    worlds = tmp_path / "worlds"
    run = worlds / "shop" / "run1"
    run.mkdir(parents=True)
    (run / "run.json").write_text(json.dumps({"status": "finished", "cost_usd": 0.1}))
    (run / "log.jsonl").write_text('{"type": "day", "date": "2024-03-01"}\nnot json\n')
    (run / "prompts.json").write_text(json.dumps({"agents": {"lena": {"prompt": "You are Lena."}}}))
    (worlds / "old").mkdir()
    (worlds / "old" / "story.md").write_text("# Story")
    (tmp_path / "secret.txt").write_text("outside")
    return worlds


def test_lists_runs_by_world(tmp_path: Path) -> None:
    server = load_server()
    worlds = make_worlds(tmp_path)
    listing = server.list_worlds(worlds)
    assert [group["world"] for group in listing] == ["old", "shop"]
    assert listing[1]["runs"][0]["id"] == "shop/run1"
    assert listing[1]["runs"][0]["status"] == "finished"
    assert listing[0]["runs"][0]["name"] == "(top)"


def test_loads_a_run_and_skips_bad_log_lines(tmp_path: Path) -> None:
    server = load_server()
    worlds = make_worlds(tmp_path)
    folder = server.resolve_run("shop/run1", worlds)
    run = server.load_run(folder, worlds, tmp_path)
    assert run["id"] == "shop/run1"
    assert run["events"] == [{"type": "day", "date": "2024-03-01"}]
    assert run["prompts"]["agents"]["lena"]["prompt"] == "You are Lena."
    assert run["records"] is None


def test_refuses_paths_outside_worlds(tmp_path: Path) -> None:
    server = load_server()
    worlds = make_worlds(tmp_path)
    assert server.resolve_run("..", worlds) is None
    assert server.resolve_run("", worlds) is None
    folder = server.resolve_run("shop/run1", worlds)
    assert server.read_file(folder, "../../../secret.txt") is None
    assert server.read_file(folder, "run.json") is not None
