"""Ask an LLM to write world.py and prompts.json, run them once without agents, fix crashes."""

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from worldgen.llm import Message, chat
from worldgen.log import RunLog
from worldgen.world import World, WorldError

INSTRUCTIONS = Path(__file__).with_name("generate.md").read_text()
TOOL_NAME = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
TOOL_KEYS = {"name", "entity", "description", "input_schema"}


def generate(
    main_prompt: str,
    run_dir: Path,
    days: int,
    model: str,
    log: RunLog,
    fix_rounds: int = 3,
    llm: Callable[..., tuple[Message, dict[str, Any]]] = chat,
) -> bool:
    """Write world.py and prompts.json into run_dir. Return whether they passed the dry run."""
    base_messages: list[Message] = [
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": f"Main prompt:\n\n{main_prompt}"},
    ]
    messages = list(base_messages)
    for attempt in range(1 + fix_rounds):
        print(f"generate: attempt {attempt + 1}, waiting for {model}...", flush=True)
        reply, usage = llm(model, messages, effort="medium")
        log.cost(usage)
        problem = _write_files(reply.get("content") or "", run_dir, usage)
        if not problem:
            problem = dry_run(run_dir, days)
        log.write({"type": "generate", "attempt": attempt + 1, "problem": problem})
        if not problem:
            print("generate: world passed the dry run", flush=True)
            return True
        print(f"generate: problem: {problem.strip().splitlines()[-1][:200]}", flush=True)
        # Keep only the latest attempt in context so earlier 50KB drafts do not bloat the prompt.
        messages = [
            *base_messages,
            reply,
            {
                "role": "user",
                "content": f"Running it failed:\n\n{problem}\n\n"
                "Fix it. Reply with both files again in full, in the same tags.",
            },
        ]
    return False


def dry_run(run_dir: Path, days: int) -> str | None:
    """Run the world's code for every day with no agents acting. Return the first problem."""
    agents = json.loads((run_dir / "prompts.json").read_text())["agents"]
    try:
        world = World(run_dir)
    except WorldError as error:
        return str(error)
    try:
        first_date = world.call("start")
        if not isinstance(first_date, str) or not first_date.strip():
            return f"start() must return a date string, got {first_date!r}"
        for day in range(days):
            if day:
                next_date = world.call("next_day")
                if not isinstance(next_date, str) or not next_date.strip():
                    return f"next_day() must return a date string, got {next_date!r}"
            acting = world.call("agents_today")
            if not isinstance(acting, list):
                return f"agents_today() must return a list, got {acting!r}"
            for agent in acting:
                if agent not in agents:
                    return f"agents_today() returned {agent!r}, which is not in prompts.json"
            for agent in agents:
                status = world.call("status", agent)
                if not isinstance(status, str):
                    return f"status({agent!r}) must return a string, got {status!r}"
                problem = _check_tools(agent, world.call("tools", agent))
                if problem:
                    return problem
        records = world.call("records")
        if not isinstance(records, dict):
            return f"records() must return a dict, got {type(records).__name__}"
        for inst, tables in records.items():
            if not isinstance(tables, dict):
                return f"records()[{inst!r}] must be a dict of tables, got {type(tables).__name__}"
            for table, rows in tables.items():
                if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
                    return f"records()[{inst!r}][{table!r}] must be a list of dict rows"
    except WorldError as error:
        return str(error)
    finally:
        world.close()
    return None


def _write_files(text: str, run_dir: Path, usage: dict[str, Any]) -> str | None:
    if usage.get("finish_reason") == "length":
        return "The reply was cut off at the output limit. Make world.py shorter."
    files = {}
    for name in ("world.py", "prompts.json"):
        matches = list(
            re.finditer(rf"<{re.escape(name)}>\s*(.*?)\s*</{re.escape(name)}>", text, re.S)
        )
        if not matches:
            return f"The reply has no <{name}>...</{name}> block."
        # Use the last matching tag block in case earlier prose mentioned the tag name,
        # and strip any wrapping markdown code fences (including trailing spaces on the fence line).
        raw = matches[-1].group(1).strip()
        files[name] = re.sub(r"^```[^\n]*\n|\n\s*```$", "", raw).strip() + "\n"
    try:
        parsed = json.loads(files["prompts.json"])
        if not isinstance(parsed, dict) or not isinstance(parsed.get("agents"), dict):
            return 'prompts.json must be {"agents": {id: {"entity": ..., "prompt": ...}}}'
        agents = parsed["agents"]
        if not agents:
            return "prompts.json: 'agents' must not be empty."
        for agent_id, agent in agents.items():
            if (
                not isinstance(agent, dict)
                or not isinstance(agent.get("prompt"), str)
                or not agent["prompt"].strip()
            ):
                return f"prompts.json: agent {agent_id!r} has no non-empty prompt string."
    except (ValueError, KeyError, AttributeError, TypeError) as error:
        return f'prompts.json is not {{"agents": {{id: {{...}}}}}}: {error}'
    for name, content in files.items():
        (run_dir / name).write_text(content)
    return None


def _check_tools(agent: str, tools: Any) -> str | None:
    if not isinstance(tools, list):
        return f"tools({agent!r}) did not return a list"
    names = set()
    for tool in tools:
        if not isinstance(tool, dict) or not set(tool) >= TOOL_KEYS:
            return f"tools({agent!r}) returned a tool without {sorted(TOOL_KEYS)}: {tool!r}"
        name = tool["name"]
        if not isinstance(name, str) or not TOOL_NAME.match(name) or name in names:
            return f"tools({agent!r}): tool name {name!r} is invalid or repeated"
        if not isinstance(tool["entity"], str) or not isinstance(tool["description"], str):
            return f"tools({agent!r}): {name} entity and description must be strings"
        if not isinstance(tool["input_schema"], dict):
            return f"tools({agent!r}): {name} input_schema is not a JSON schema object"
        names.add(name)
    return None
