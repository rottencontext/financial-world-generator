"""worldgen run PROMPT_FILE: generate a world from the prompt and simulate its time range."""

import json
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any

import typer

from worldgen import claude_cli, llm
from worldgen.generate import generate
from worldgen.log import RunLog
from worldgen.simulate import simulate

app = typer.Typer(add_completion=False)


class Backend(StrEnum):
    """Who answers a stage's model calls, and so who pays for them."""

    openrouter = "openrouter"  # OPENROUTER_API_KEY, billed per token
    claude = "claude"  # the `claude` CLI's login: a Claude subscription or its API key


CHAT: dict[Backend, Callable[..., tuple[llm.Message, dict[str, Any]]]] = {
    Backend.openrouter: llm.chat,
    Backend.claude: claude_cli.chat,
}
DEFAULT_MODELS = {  # (writes the world, plays the agents)
    Backend.openrouter: ("z-ai/glm-5.3", "z-ai/glm-5.3-flash"),
    Backend.claude: ("opus", "sonnet"),
}


def run_name(world_model: str, agent_model: str, now: datetime) -> str:
    """The default run folder: when the run started, who wrote the world and who played the agents,
    e.g. 20261105-183950_world-fable_agents-opus. A model id keeps only its last path segment."""
    world, agents = (model.rsplit("/", 1)[-1] for model in (world_model, agent_model))
    return f"{now:%Y%m%d-%H%M%S}_world-{world}_agents-{agents}"


@app.callback()
def main() -> None:
    """A financial world generator."""


@app.command()
def run(
    prompt_file: Path,
    out: Annotated[
        Path | None,
        typer.Option(help="Default: worlds/<prompt>/<time>_world-<model>_agents-<model>."),
    ] = None,
    world_backend: Annotated[
        Backend, typer.Option(help="Answers the world-writing call.")
    ] = Backend.openrouter,
    world_model: Annotated[
        str | None,
        typer.Option(
            help="Writes the world. Default: z-ai/glm-5.3, or opus with --world-backend claude."
        ),
    ] = None,
    agent_backend: Annotated[
        Backend, typer.Option(help="Answers the agents' calls.")
    ] = Backend.openrouter,
    agent_model: Annotated[
        str | None,
        typer.Option(
            help="Plays the agents. Default: z-ai/glm-5.3-flash, "
            "or sonnet with --agent-backend claude."
        ),
    ] = None,
    fix_rounds: Annotated[int, typer.Option(help="Times a crashing world goes back.")] = 5,
) -> None:
    """Generate a world from PROMPT_FILE and simulate the time range the prompt names."""
    world_model = world_model or DEFAULT_MODELS[world_backend][0]
    agent_model = agent_model or DEFAULT_MODELS[agent_backend][1]
    prompt_text = prompt_file.read_text()
    name = prompt_file.stem if prompt_file.stem != "PROMPT" else prompt_file.parent.name
    run_dir = out or Path("worlds") / name / run_name(world_model, agent_model, datetime.now())
    run_dir.mkdir(parents=True, exist_ok=False)
    log = RunLog(run_dir / "log.jsonl")
    summary: dict[str, object] = {
        "prompt": str(prompt_file),
        "world_model": world_model,
        "world_backend": world_backend.value,
        "agent_model": agent_model,
        "agent_backend": agent_backend.value,
    }
    try:
        if generate(prompt_text, run_dir, world_model, log, fix_rounds, llm=CHAT[world_backend]):
            summary.update(simulate(run_dir, agent_model, log, llm=CHAT[agent_backend]))
        else:
            summary["status"] = "stopped: the world kept crashing in the dry run"
    except Exception as error:
        summary["status"] = f"stopped: {error!r}"
        raise
    finally:
        summary["cost_usd"] = round(log.cost_usd, 4)
        (run_dir / "run.json").write_text(json.dumps(summary, indent=1))
        log.close()
    print(f"{summary.get('status')}: {run_dir} (${log.cost_usd:.2f})")


if __name__ == "__main__":
    app()
