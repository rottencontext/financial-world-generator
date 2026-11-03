"""worldgen PROMPT_FILE: generate a world from the prompt and simulate the prompt's time range."""

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from worldgen.generate import generate
from worldgen.log import RunLog
from worldgen.simulate import simulate

app = typer.Typer(add_completion=False)


@app.command()
def run(
    prompt_file: Path,
    out: Annotated[Path | None, typer.Option(help="Default: worlds/<prompt>/<time>.")] = None,
    world_model: Annotated[str, typer.Option(help="Writes the world.")] = "z-ai/glm-5.3",
    agent_model: Annotated[str, typer.Option(help="Plays the agents.")] = "z-ai/glm-5.3-flash",
    fix_rounds: Annotated[int, typer.Option(help="Times a crashing world goes back.")] = 5,
) -> None:
    prompt_text = prompt_file.read_text()
    name = prompt_file.stem if prompt_file.stem != "PROMPT" else prompt_file.parent.name
    run_dir = out or Path("worlds") / name / datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)
    log = RunLog(run_dir / "log.jsonl")
    summary: dict[str, object] = {
        "prompt": str(prompt_file),
        "world_model": world_model,
        "agent_model": agent_model,
    }
    try:
        if generate(prompt_text, run_dir, world_model, log, fix_rounds):
            summary.update(simulate(run_dir, agent_model, log))
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
