"""worldgen command line.

uv run --env-file .env worldgen narrate --prompt-file TARGET_EXAMPLE.md --out worlds/lumen/story
"""

import asyncio
from collections import Counter
from pathlib import Path
from typing import Annotated, Any

import typer
from pydantic import ValidationError

from worldgen.llm.base import LlmConfigError
from worldgen.llm.factory import create_llm
from worldgen.llm.settings import DEFAULT_EFFORT, Effort, Provider, settings_for
from worldgen.policies import Policies
from worldgen.sinks.run_log import RunLog
from worldgen.tree.expand import expand as expand_tree
from worldgen.tree.nodes import Node, Tree
from worldgen.tree.render import render

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="worldgen: generate financial worlds with LLM agents.",
)


@app.callback()
def _commands() -> None:
    """Keeps narrate a named subcommand while it is the only one."""


ProviderOpt = Annotated[
    Provider | None,
    typer.Option(
        help=("Model provider. Auto-detects credentials in order: anthropic, deepseek, openrouter.")
    ),
]
ModelOpt = Annotated[
    str | None,
    typer.Option(help="Model id. Uses the selected provider's default when omitted (see README)."),
]
EffortOpt = Annotated[
    Effort,
    typer.Option(help="How hard the model thinks. OpenRouter maps xhigh/max to high."),
]
PolicyOpt = Annotated[
    list[str] | None,
    typer.Option("--policy", help="Switch a policy, as name=option. Repeatable."),
]
MaxStepsOpt = Annotated[int, typer.Option(min=1, help="Model calls allowed per narrator turn.")]
MaxTokensOpt = Annotated[
    int | None,
    typer.Option(min=1, help="Output token limit per model call. Default: 64000."),
]


@app.command()
def narrate(
    out: Annotated[Path, typer.Option(help="New directory for tree.json, story.md and log.jsonl.")],
    prompt: Annotated[str | None, typer.Option(help="What the starting narrator tells.")] = None,
    prompt_file: Annotated[
        Path | None, typer.Option(exists=True, dir_okay=False, help="The prompt, read from a file.")
    ] = None,
    brief: Annotated[
        str | None,
        typer.Option(help="What is going on, when the prompt is one part of a larger world."),
    ] = None,
    brief_file: Annotated[
        Path | None, typer.Option(exists=True, dir_okay=False, help="The brief, read from a file.")
    ] = None,
    name: Annotated[str, typer.Option(help="The starting narrator's name.")] = "Root narrator",
    provider: ProviderOpt = None,
    model: Annotated[str | None, ModelOpt] = None,
    effort: EffortOpt = DEFAULT_EFFORT,
    policy: PolicyOpt = None,
    max_steps: MaxStepsOpt = 30,
    max_tokens: MaxTokensOpt = None,
) -> None:
    """Start a new story tree: one narrator expands a prompt, then every narrator below it."""
    prompt_text = _text(prompt, prompt_file, "prompt")
    if prompt_text is None:
        raise typer.BadParameter("give --prompt or --prompt-file")
    if (out / "tree.json").exists():
        raise typer.BadParameter(f"{out} already holds a tree; choose a new --out directory")
    out.mkdir(parents=True, exist_ok=True)
    tree = Tree.new(prompt_text, _text(brief, brief_file, "brief"), name)
    _run(tree, out, provider, model, effort, policy, max_steps, max_tokens)


def _run(
    tree: Tree,
    out: Path,
    provider: Provider | None,
    model: str | None,
    effort: Effort,
    policy: list[str] | None,
    max_steps: int,
    max_tokens: int | None = None,
) -> None:
    policies = _policies(policy or [])
    try:
        settings = settings_for(provider, model, effort, max_tokens=max_tokens)
        llm = create_llm(settings)
    except LlmConfigError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(1) from error
    log = RunLog(out / "log.jsonl")
    log.write(
        "run_started",
        llm=llm.name,
        effort=effort,
        max_tokens=settings.max_tokens,
        policies=policies.model_dump(),
    )
    typer.echo(f"Using {llm.name}, effort {effort}. Narrating {tree.root}.")

    def save() -> None:
        tree.save(out / "tree.json")
        (out / "story.md").write_text(render(tree))

    save()

    asyncio.run(expand_tree(tree, tree.root, llm, log, policies, max_steps, save))
    log.write("run_finished")
    save()
    _summary(tree, log.entries, out)


def _summary(tree: Tree, entries: list[dict[str, Any]], out: Path) -> None:
    typer.echo("")
    _outline(tree, tree.node(tree.root), 0)
    failures = [e for e in entries if e["kind"] == "turn_finished" and e["status"] != "done"]
    for entry in failures:
        typer.echo(f"  ! {entry['node']} {entry['status']}: {entry['reason']}")
    usage: Counter[str] = Counter()
    calls = 0
    for entry in entries:
        if entry["kind"] == "llm_reply":
            calls += 1
            for key in ("input_tokens", "output_tokens", "cache_read_input_tokens"):
                usage[key] += entry["usage"].get(key) or 0
    typer.echo(
        f"\nModel calls: {calls}. Tokens in: {usage['input_tokens']}, "
        f"cached: {usage['cache_read_input_tokens']}, out: {usage['output_tokens']}."
    )
    pending = tree.pending_narrators()
    if pending:
        typer.echo(
            f"Narrators that never ran, because a narrator above failed: {', '.join(pending)}."
        )
    typer.echo(f"Wrote {out / 'tree.json'}, {out / 'story.md'} and {out / 'log.jsonl'}.")


def _outline(tree: Tree, node: Node, indent: int) -> None:
    status = "actor" if node.role == "actor" else node.status
    extras = []
    if node.story:
        extras.append(f"story {len(node.story.split())} words")
    if node.children:
        extras.append(f"{len(node.children)} children")
    detail = f" ({', '.join(extras)})" if extras else ""
    typer.echo(f"{'  ' * indent}{node.id}  {node.name}  [{status}]{detail}")
    for child in node.children:
        _outline(tree, tree.node(child), indent + 1)


def _text(value: str | None, path: Path | None, label: str) -> str | None:
    if value is not None and path is not None:
        raise typer.BadParameter(f"give --{label} or --{label}-file, not both")
    if path is not None:
        return path.read_text()
    return value


def _policies(pairs: list[str]) -> Policies:
    values: dict[str, str] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise typer.BadParameter(f"--policy takes name=option, got {pair!r}")
        values[key.strip()] = value.strip()
    try:
        return Policies.model_validate(values)
    except ValidationError as error:
        raise typer.BadParameter(str(error)) from error
