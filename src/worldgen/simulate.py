"""The day loop: each day the agents that wake act through the world's tools, then the clock advances."""

import copy
import json
import re
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from worldgen.llm import Message, chat
from worldgen.log import RunLog
from worldgen.world import MAX_DAYS, World, WorldError

TURN_RULES = """\
Each turn is one day. You act only through your tools, and you know only what your status, \
your plans, your notes and your recent tool results tell you. Before each tool call, say in \
one sentence why. Use the `memory` tool to add, update or mark done dated plans (which stay \
until you mark them done) and to add, replace or remove notes (which are automatically dated \
with today's date). Do nothing if nothing needs doing today. When you are done, reply without \
a tool call: that reply goes only into the log and does not change your plans or notes."""

MAX_CALLS = 15
MAX_PLANS = 25
MAX_NOTES = 15
RECENT_DAYS = 3
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATED_LINE = re.compile(r"^(\d{4}-\d{2}-\d{2})\s*:\s*(.+)$")

MEMORY_TOOL = {
    "type": "function",
    "function": {
        "name": "memory",
        "description": (
            "[runner] Manage your persistent plans and dated notes. "
            "A plan stays until you mark it done. Every note is automatically stamped with today's date."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "add_plan",
                        "update_plan",
                        "done_plan",
                        "add_note",
                        "replace_note",
                        "remove_note",
                    ],
                    "description": "Operation to perform on your plans or notes.",
                },
                "id": {
                    "type": "string",
                    "description": "Plan id (e.g. 'p1') or note id (e.g. 'n1') for update_plan, done_plan, replace_note or remove_note.",
                },
                "due": {
                    "type": "string",
                    "description": "Plan date as YYYY-MM-DD (required for add_plan, optional for update_plan).",
                },
                "text": {
                    "type": "string",
                    "description": "Plan task or note text (required for add_plan, add_note and replace_note; optional for update_plan).",
                },
            },
            "required": ["action"],
        },
    },
}


def init_memory(
    agent_spec: dict[str, Any], start_date: str
) -> tuple[dict[str, list[dict[str, str]]], dict[str, int]]:
    """Build initial {plans, notes} and monotonic ID counters for one agent."""
    plans: list[dict[str, str]] = []
    notes: list[dict[str, str]] = []
    raw_plans = agent_spec.get("plans")
    raw_notes = agent_spec.get("notes")

    if isinstance(raw_plans, list):
        for item in raw_plans:
            if isinstance(item, dict):
                task = str(item.get("task") or item.get("text") or "").strip()
                due = str(item.get("due") or item.get("date") or start_date).strip()
            else:
                line = str(item).strip()
                match = DATED_LINE.match(line)
                due, task = (match.group(1), match.group(2).strip()) if match else (start_date, line)
            if task:
                plans.append({"id": f"p{len(plans) + 1}", "due": due, "task": task})

    if isinstance(raw_notes, list):
        for item in raw_notes:
            if isinstance(item, dict):
                text = str(item.get("text") or "").strip()
                note_date = str(item.get("date") or start_date).strip()
            else:
                line = str(item).strip()
                match = DATED_LINE.match(line)
                note_date, text = (
                    (match.group(1), match.group(2).strip()) if match else (start_date, line)
                )
            if text:
                notes.append({"id": f"n{len(notes) + 1}", "date": note_date, "text": text})

    # Legacy fallback: seed non-empty lines from "notepad" as initial plans on start_date.
    if not plans and not notes and isinstance(agent_spec.get("notepad"), str):
        for raw_line in agent_spec["notepad"].splitlines():
            line = re.sub(r"^[-*•]\s+", "", raw_line.strip())
            if not line:
                continue
            match = DATED_LINE.match(line)
            due, task = (match.group(1), match.group(2).strip()) if match else (start_date, line)
            plans.append({"id": f"p{len(plans) + 1}", "due": due, "task": task})

    return {"plans": plans, "notes": notes}, {"p": len(plans) + 1, "n": len(notes) + 1}


def format_plans(plans: list[dict[str, str]], today: str) -> str:
    if not plans:
        return "(none)"
    lines = []
    for plan in plans:
        due = plan["due"]
        flag = " [DUE]" if due <= today else ""
        lines.append(f"- [{plan['id']}] {due}{flag}: {plan['task']}")
    return "\n".join(lines)


def format_notes(notes: list[dict[str, str]]) -> str:
    if not notes:
        return "(none)"
    return "\n".join(f"- [{note['id']}] {note['date']}: {note['text']}" for note in notes)


def format_memory(mem: dict[str, list[dict[str, str]]], today: str) -> str:
    return f"Plans:\n{format_plans(mem['plans'], today)}\n\nNotes:\n{format_notes(mem['notes'])}"


def _clean_note_text(text: str, date: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith(f"{date}:"):
        cleaned = cleaned[len(date) + 1 :].strip()
    return cleaned


def apply_memory(
    mem: dict[str, list[dict[str, str]]],
    counters: dict[str, int],
    date: str,
    args: dict[str, Any],
) -> str:
    """Execute a memory tool call against the agent's plans and dated notes."""
    action = str(args.get("action") or "").strip()
    item_id = str(args.get("id") or "").strip()
    due = str(args.get("due") or args.get("date") or "").strip()
    text = str(args.get("text") if args.get("text") is not None else args.get("task") or "").strip()

    if action == "add_plan":
        if not ISO_DATE.match(due):
            return "Error: add_plan requires 'due' as YYYY-MM-DD."
        if not text:
            return "Error: add_plan requires non-empty 'text'."
        if len(mem["plans"]) >= MAX_PLANS:
            return (
                f"Rejected: you already have {MAX_PLANS} active plans. "
                "Mark completed plans done with done_plan or update an existing plan first."
            )
        plan_id = f"p{counters['p']}"
        counters["p"] += 1
        mem["plans"].append({"id": plan_id, "due": due, "task": text})
        return f"Added plan {plan_id} (due {due}): {text}"

    if action == "update_plan":
        plan = next((p for p in mem["plans"] if p["id"] == item_id), None)
        if plan is None:
            return f"Error: no active plan with id {item_id!r}."
        if not due and not text:
            return "Error: update_plan requires a new 'due' (YYYY-MM-DD) or 'text'."
        if due:
            if not ISO_DATE.match(due):
                return "Error: 'due' must be YYYY-MM-DD."
            plan["due"] = due
        if text:
            plan["task"] = text
        return f"Updated plan {plan['id']} (due {plan['due']}): {plan['task']}"

    if action == "done_plan":
        for index, plan in enumerate(mem["plans"]):
            if plan["id"] == item_id:
                removed = mem["plans"].pop(index)
                return f"Marked plan {item_id} done: {removed['task']}"
        return f"Error: no active plan with id {item_id!r}."

    if action == "add_note":
        cleaned = _clean_note_text(text, date)
        if not cleaned:
            return "Error: add_note requires non-empty 'text'."
        if len(mem["notes"]) >= MAX_NOTES:
            return (
                f"Rejected: you already have {MAX_NOTES} notes. "
                "Use replace_note or remove_note instead."
            )
        note_id = f"n{counters['n']}"
        counters["n"] += 1
        mem["notes"].append({"id": note_id, "date": date, "text": cleaned})
        return f"Added note {note_id} ({date}): {cleaned}"

    if action == "replace_note":
        cleaned = _clean_note_text(text, date)
        if not cleaned:
            return "Error: replace_note requires non-empty 'text'."
        note = next((n for n in mem["notes"] if n["id"] == item_id), None)
        if note is None:
            return f"Error: no note with id {item_id!r}."
        note["date"] = date
        note["text"] = cleaned
        return f"Replaced note {item_id} ({date}): {cleaned}"

    if action == "remove_note":
        for index, note in enumerate(mem["notes"]):
            if note["id"] == item_id:
                mem["notes"].pop(index)
                return f"Removed note {item_id}."
        return f"Error: no note with id {item_id!r}."

    return (
        f"Error: unknown memory action {action!r}. "
        "Use add_plan, update_plan, done_plan, add_note, replace_note or remove_note."
    )


def simulate(
    run_dir: Path,
    model: str,
    log: RunLog,
    llm: Callable[..., tuple[Message, dict[str, Any]]] = chat,
) -> dict[str, Any]:
    """Run the world from start() until next_day() returns None, saving its records each day.
    Return a summary for run.json."""
    agents = json.loads((run_dir / "prompts.json").read_text())["agents"]
    memories: dict[str, dict[str, list[dict[str, str]]]] = {}
    counters: dict[str, dict[str, int]] = {}
    recent: dict[str, list[tuple[str, str]]] = {agent_id: [] for agent_id in agents}
    lock = threading.Lock()
    count_lock = threading.Lock()
    counts = {"calls": 0, "crashes": 0, "turns": 0, "failed_turns": 0}
    world = World(run_dir)
    summary: dict[str, Any] = {"status": "finished"}

    def world_call(op: str, *args: Any) -> Any:
        with lock:
            return world.call(op, *args)

    def bump(name: str) -> None:
        with count_lock:
            counts[name] += 1

    def safe_turn(agent: str, date: str) -> None:
        try:
            turn(agent, date)
        except Exception as error:  # a failed model call ends this turn, not the run
            bump("failed_turns")
            log.write({"type": "turn_failed", "date": date, "agent": agent, "error": repr(error)})
            print(f"  {agent}: turn failed: {error!r}"[:200], flush=True)

    def turn(agent: str, date: str) -> None:
        try:
            status = world_call("status", agent)
            tools = world_call("tools", agent)
        except WorldError as error:
            log.write({"type": "crash", "date": date, "agent": agent, "error": str(error)})
            bump("crashes")
            return
        by_name = {tool["name"]: tool for tool in tools}
        functions = [
            *[
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": f"[{tool['entity']}] {tool['description']}",
                        "parameters": tool["input_schema"],
                    },
                }
                for tool in tools
            ],
            MEMORY_TOOL,
        ]
        dates = sorted({d for d, _ in recent[agent]})[-RECENT_DAYS:]
        history = "\n".join(line for d, line in recent[agent] if d in dates) or "(none)"
        mem = memories[agent]
        messages: list[Message] = [
            {"role": "system", "content": f"{agents[agent]['prompt']}\n\n{TURN_RULES}"},
            {
                "role": "user",
                "content": f"Today is {date}.\n\n## Status\n{status}\n\n"
                f"## Your plans (stay until you mark them done)\n{format_plans(mem['plans'], date)}\n\n"
                f"## Your notes (dated observations)\n{format_notes(mem['notes'])}\n\n"
                f"## Your calls in the last {RECENT_DAYS} days\n{history}",
            },
        ]
        calls = 0
        reply_text = ""
        while True:
            out_of_calls = calls >= MAX_CALLS
            reply, usage = llm(
                model, messages, functions or None, tool_choice="none" if out_of_calls else None
            )
            log.cost(usage)
            messages.append(reply)
            tool_calls = [] if out_of_calls else reply.get("tool_calls") or []
            if not tool_calls:
                reply_text = (reply.get("content") or "").strip()
                break
            why = (reply.get("content") or "").strip() or (reply.get("reasoning") or "")[:400]
            for tool_call in tool_calls:
                fn = tool_call.get("function") or {}
                name = fn.get("name") or ""
                call_id = tool_call.get("id") or ""
                if calls >= MAX_CALLS:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": "Skipped: daily tool call limit reached.",
                        }
                    )
                    continue
                event: dict[str, Any] = {"type": "call", "date": date, "agent": agent, "tool": name}
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                    if not isinstance(args, dict):
                        args, result = None, "Error: the arguments must be a JSON object."
                except ValueError:
                    args, result = None, "Error: the arguments were not valid JSON."
                if args is not None and name == "memory":
                    event["entity"] = "runner"
                    result = apply_memory(mem, counters[agent], date, args)
                elif args is not None and name not in by_name:
                    result = f"Error: you have no tool named {name} today."
                elif args is not None:
                    event["entity"] = by_name[name]["entity"]
                    try:
                        result = str(world_call("call_tool", agent, name, args))
                    except WorldError as error:
                        # The traceback's last line names the problem (e.g. a "$95.00" it could
                        # not parse), so the agent can change its arguments instead of retrying.
                        last = (str(error).strip().splitlines() or ["unknown error"])[-1]
                        result = f"Error: the world's code crashed on this call: {last[:300]}"
                        event["crash"] = str(error)
                        bump("crashes")
                event.update(args=args, why=why, result=result)
                log.write(event)
                bump("calls")
                print(f"  {agent} -> {name}: {result[:120]!r}", flush=True)
                recent[agent].append((date, f"{date} {name}({json.dumps(args)}) -> {result[:300]}"))
                messages.append({"role": "tool", "tool_call_id": call_id, "content": result})
                calls += 1
            if calls >= MAX_CALLS:
                messages.append(
                    {"role": "user", "content": "No more calls today. Reply to finish your turn."}
                )
        bump("turns")
        log.write(
            {
                "type": "turn",
                "date": date,
                "agent": agent,
                "calls": calls,
                "reply": reply_text,
                "memory": copy.deepcopy(mem),
                "notepad": format_memory(mem, date),
            }
        )

    def save_records() -> None:
        records = world.call("records")
        (run_dir / "records.json").write_text(json.dumps(records, indent=1, default=str))

    try:
        date = world.call("start")
        summary["first_date"] = date
        for agent_id, agent_spec in agents.items():
            memories[agent_id], counters[agent_id] = init_memory(agent_spec, date)
        for _ in range(MAX_DAYS):
            raw_acting = world.call("agents_today")
            if not isinstance(raw_acting, list):
                raise WorldError(f"agents_today() must return a list, got {raw_acting!r}")
            deduped = list(dict.fromkeys(raw_acting))
            unknown = [agent for agent in deduped if agent not in agents]
            acting = [agent for agent in deduped if agent in agents]
            print(f"{date}: {len(acting)} agents act", flush=True)
            log.write({"type": "day", "date": date, "agents": acting, "unknown": unknown})
            if acting:
                with ThreadPoolExecutor(max_workers=min(8, len(acting))) as pool:
                    list(pool.map(safe_turn, acting, [date] * len(acting)))
            summary["last_date"] = date
            save_records()
            (run_dir / "notepads.json").write_text(json.dumps(memories, indent=1))
            date = world.call("next_day")
            if date is None:
                break
        else:
            raise WorldError(f"next_day() still returned a date after {MAX_DAYS} days")
    except WorldError as error:
        bump("crashes")
        summary["status"] = "stopped: the world's code crashed"
        log.write({"type": "crash", "error": str(error)})
        print(f"stopped: {str(error).strip().splitlines()[-1]}", flush=True)
    finally:
        world.close()
        if not memories:
            for agent_id, agent_spec in agents.items():
                memories[agent_id], counters[agent_id] = init_memory(agent_spec, "1970-01-01")
        (run_dir / "notepads.json").write_text(json.dumps(memories, indent=1))
    return {**summary, **counts}
