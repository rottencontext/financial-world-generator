"""Ask an LLM to write world.py and prompts.json, dry-run every tool, send crashes back to fix."""

import itertools
import json
import random
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from worldgen.llm import Message, chat
from worldgen.log import RunLog
from worldgen.world import MAX_DAYS, World, WorldError

INSTRUCTIONS = Path(__file__).with_name("generate.md").read_text()
TOOL_NAME = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
TOOL_KEYS = {"name", "entity", "description", "input_schema"}


def generate(
    main_prompt: str,
    run_dir: Path,
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
            problem = dry_run(run_dir)
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


def dry_run(run_dir: Path, passes: int = 3) -> str | None:
    """Run the world's code for every day from start() until next_day() returns None, calling
    each acting agent's tools with plain and messy arguments. Return the first problem.

    Calls change the world (a payment marks an invoice paid, so a later credit request on it is
    refused), so each pass starts a fresh world and shuffles the order of the tools each day."""
    for seed in range(passes):
        problem = _dry_pass(run_dir, random.Random(seed))
        if problem:
            return problem
    return None


def _dry_pass(run_dir: Path, rng: random.Random) -> str | None:
    agents = json.loads((run_dir / "prompts.json").read_text())["agents"]
    try:
        world = World(run_dir)
    except WorldError as error:
        return str(error)
    # Ids the agents could see so far, most recently seen last, so tools reach real records.
    seen: dict[str, None] = {}
    doing = "start()"
    try:
        date = world.call("start")
        if not isinstance(date, str) or not date.strip():
            return f"start() must return a date string, got {date!r}"
        for _ in range(MAX_DAYS):
            doing = f"agents_today() on {date}"
            acting = world.call("agents_today")
            if not isinstance(acting, list):
                return f"agents_today() must return a list, got {acting!r}"
            for agent in acting:
                if agent not in agents:
                    return f"agents_today() returned {agent!r}, which is not in prompts.json"
            toolsets = {}
            for agent in agents:
                doing = f"status({agent!r}) on {date}"
                status = world.call("status", agent)
                if not isinstance(status, str):
                    return f"status({agent!r}) must return a string, got {status!r}"
                _remember_ids(seen, status)
                doing = f"tools({agent!r}) on {date}"
                toolsets[agent] = world.call("tools", agent)
                problem = _check_tools(agent, toolsets[agent])
                if problem:
                    return problem
            calls = [(agent, tool) for agent in dict.fromkeys(acting) for tool in toolsets[agent]]
            rng.shuffle(calls)
            for agent, tool in calls:
                ids = [*list(seen)[-MAX_IDS:], *agents]
                for args in _arg_sets(tool["input_schema"], ids, date):
                    doing = f"call_tool({agent!r}, {tool['name']!r}, {json.dumps(args)}) on {date}"
                    _remember_ids(seen, str(world.call("call_tool", agent, tool["name"], args)))
            doing = f"next_day() after {date}"
            date = world.call("next_day")
            if date is None:
                break
            if not isinstance(date, str) or not date.strip():
                return f"next_day() must return a date string or None, got {date!r}"
        else:
            return (
                f"next_day() still returned a date after {MAX_DAYS} days. "
                "Return None after the main prompt's last day."
            )
        doing = "records()"
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
        return f"The dry run crashed in {doing}:\n\n{error}"
    finally:
        world.close()
    return None


# Dry run arguments. Each argument gets a plain value, messy forms an agent might send, and other
# valid choices; argument names decide which kind of value fits.
MAX_IDS = 30
MAX_ID_COMBOS = 30  # only when a tool takes two or more ids
# "AR-1", "INV_2041", or a bare number such as invoice "2417" that is not part of an amount or date.
ID_TOKEN = re.compile(r"\b[A-Za-z]+[-_#]?\d[\w-]*|(?<![\w$.,/-])\d{3,}(?![\w/-]|[.,]\d)")
ID_NAME = re.compile(r"(^|_)(id|no|num|number|ref|reference)$|id$", re.I)
MONEY_NAME = re.compile(
    r"amount|price|total|cost|fee|credit|debit|payment|balance|wage|salary", re.I
)
DATE_NAME = re.compile(r"date|day|when|until|deadline", re.I)
TEXT_NAME = re.compile(
    r"note|reason|text|message|description|memo|evidence|comment|body|subject|detail|summary",
    re.I,
)


def _remember_ids(seen: dict[str, None], text: str) -> None:
    for token in ID_TOKEN.findall(text):
        seen.pop(token, None)
        seen[token] = None


def _values(name: str, spec: dict[str, Any], date: str) -> tuple[Any, list[Any], list[Any]] | None:
    """(plain value, messy forms, other valid choices), or None for an id-like argument."""
    kind = spec.get("type")
    if isinstance(spec.get("enum"), list) and spec["enum"]:
        return spec["enum"][0], [], spec["enum"][1:]
    if kind == "boolean":
        return True, [], [False]
    if kind in ("array", "object"):
        return ([] if kind == "array" else {}), [], []
    if ID_NAME.search(name):
        return None
    if MONEY_NAME.search(name) or "$" in str(spec.get("description", "")):
        return "10.00", ["$10.00", "1,000.00", 10], []
    if kind == "integer":
        return 1, ["1"], []
    if kind == "number":
        return 10, ["10"], []
    if DATE_NAME.search(name):
        return date, ["tomorrow"], []
    if TEXT_NAME.search(name):
        return "Dry run test.", [], []
    return None


def _arg_sets(schema: Any, ids: list[str], date: str) -> list[dict[str, Any]]:
    """Argument sets for one tool: for each mix of seen ids, the messy forms first (before a plain
    call uses up the record), then other choices, then required arguments only, then plain."""
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict) or not props:
        return [{}]
    required = set(schema.get("required") or [])
    values = {n: _values(n, s if isinstance(s, dict) else {}, date) for n, s in props.items()}
    id_fields = [n for n, v in values.items() if v is None]
    combos = list(itertools.islice(itertools.product(ids, repeat=len(id_fields)), 10_000))
    if len(id_fields) > 1 and len(combos) > MAX_ID_COMBOS:
        combos = random.Random(0).sample(combos, MAX_ID_COMBOS)
    plain = {n: v[0] for n, v in values.items() if v is not None}
    messy = [{n: m} for n, v in values.items() if v is not None for m in v[1]]
    others = [{n: o} for n, v in values.items() if v is not None for o in v[2]]
    sets = []
    for combo in combos:
        base = {**plain, **dict(zip(id_fields, combo, strict=True))}
        sets += [{**base, **change} for change in messy + others]
        sets += [{n: base[n] for n in base if n in required}, base]
    unique = {json.dumps(args, sort_keys=True): args for args in sets}
    return list(unique.values())


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
