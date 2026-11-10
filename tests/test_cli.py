"""The command line: which backend answers each stage, and the model each one defaults to."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from worldgen import claude_cli, cli, llm


@pytest.fixture
def stages(monkeypatch: pytest.MonkeyPatch) -> dict[str, tuple[str, Any]]:
    """Replace generate and simulate with fakes that record the model and llm they got."""
    seen: dict[str, tuple[str, Any]] = {}

    def fake_generate(
        prompt: str, run_dir: Path, model: str, log: Any, rounds: int, llm: Any
    ) -> bool:
        seen["generate"] = (model, llm)
        return True

    def fake_simulate(run_dir: Path, model: str, log: Any, llm: Any) -> dict[str, Any]:
        seen["simulate"] = (model, llm)
        return {"status": "finished"}

    monkeypatch.setattr(cli, "generate", fake_generate)
    monkeypatch.setattr(cli, "simulate", fake_simulate)
    return seen


def invoke(tmp_path: Path, *options: str) -> dict[str, Any]:
    prompt = tmp_path / "PROMPT.md"
    prompt.write_text("A tiny company.")
    out = tmp_path / "run"
    result = CliRunner().invoke(cli.app, ["run", str(prompt), "--out", str(out), *options])
    assert result.exit_code == 0, result.output
    summary: dict[str, Any] = json.loads((out / "run.json").read_text())
    return summary


def test_openrouter_is_the_default_for_both_stages(tmp_path: Path, stages: dict[str, Any]) -> None:
    summary = invoke(tmp_path)

    assert stages["generate"] == ("z-ai/glm-5.3", llm.chat)
    assert stages["simulate"] == ("z-ai/glm-5.3-flash", llm.chat)
    assert summary["world_backend"] == "openrouter" and summary["agent_backend"] == "openrouter"


def test_each_stage_picks_its_backend_and_that_backend_s_default_model(
    tmp_path: Path, stages: dict[str, Any]
) -> None:
    summary = invoke(tmp_path, "--world-backend", "claude", "--agent-model", "openai/gpt-5")

    assert stages["generate"] == ("opus", claude_cli.chat)
    assert stages["simulate"] == ("openai/gpt-5", llm.chat)
    assert summary["world_backend"] == "claude" and summary["world_model"] == "opus"
    assert summary["agent_backend"] == "openrouter" and summary["agent_model"] == "openai/gpt-5"


def test_a_named_model_overrides_the_claude_default(tmp_path: Path, stages: dict[str, Any]) -> None:
    invoke(tmp_path, "--agent-backend", "claude", "--agent-model", "fable")

    assert stages["generate"] == ("z-ai/glm-5.3", llm.chat)
    assert stages["simulate"] == ("fable", claude_cli.chat)


def test_the_default_folder_names_the_time_and_both_models() -> None:
    started = datetime(2026, 11, 5, 18, 39, 50)

    assert cli.run_name("fable", "opus", started) == "20261105-183950_world-fable_agents-opus"
    assert (
        cli.run_name("anthropic/claude-opus-5.5", "z-ai/glm-5.3-flash", started)
        == "20261105-183950_world-claude-opus-5.5_agents-glm-5.3-flash"
    )
