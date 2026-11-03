"""The day loop: the world's automated code runs, then the agents it wakes act through its tools."""

import json
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from worldgen.llm import Message, chat
from worldgen.log import RunLog
from worldgen.world import World, WorldError

TURN_RULES = """\
Each turn is one day. You act only through your tools, and you know only what your status, \
your notepad and your tool results tell you. Before each tool call, say in one sentence why. \
Do nothing if nothing needs doing today. When you are done, reply without a tool call: \
that reply becomes your notepad for tomorrow (active plans and open items, under 150 words)."""

MAX_CALLS = 15
RECENT_DAYS = 3


def simulate(
    run_dir: Path,
    days: int,
    model: str,
    log: RunLog,
    llm: Callable[..., tuple[Message, dict[str, Any]]] = chat,
) -> dict[str, Any]:
    """Run the world for `days` days and save its records. Return a summary for run.json."""
    agents = json.loads((run_dir / "prompts.json").read_text())["agents"]
    notepads = {agent_id: agent.get("notepad", "") for agent_id, agent in agents.items()}
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
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": f"[{tool['entity']}] {tool['description']}",
                    "parameters": tool["input_schema"],
                },
            }
            for tool in tools
        ]
        dates = sorted({d for d, _ in recent[agent]})[-RECENT_DAYS:]
        history = "\n".join(line for d, line in recent[agent] if d in dates) or "(none)"
        messages: list[Message] = [
            {"role": "system", "content": f"{agents[agent]['prompt']}\n\n{TURN_RULES}"},
            {
                "role": "user",
                "content": f"Today is {date}.\n\n## Status\n{status}\n\n"
                f"## Your notepad\n{notepads[agent] or '(empty)'}\n\n"
                f"## Your calls in the last {RECENT_DAYS} days\n{history}",
            },
        ]
        calls = 0
        while True:
            out_of_calls = calls >= MAX_CALLS
            reply, usage = llm(
                model, messages, functions or None, tool_choice="none" if out_of_calls else None
            )
            log.cost(usage)
            messages.append(reply)
            tool_calls = [] if out_of_calls else reply.get("tool_calls") or []
            if not tool_calls:
                notepads[agent] = (reply.get("content") or "").strip() or notepads[agent]
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
                if args is not None and name not in by_name:
                    result = f"Error: you have no tool named {name} today."
                elif args is not None:
                    event["entity"] = by_name[name]["entity"]
                    try:
                        result = str(world_call("call_tool", agent, name, args))
                    except WorldError as error:
                        result = "Error: that call failed inside the world's code."
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
                    {"role": "user", "content": "No more calls today. Reply with your notepad."}
                )
        bump("turns")
        log.write(
            {
                "type": "turn",
                "date": date,
                "agent": agent,
                "calls": calls,
                "notepad": notepads[agent],
            }
        )

    try:
        date = world.call("start")
        summary["first_date"] = date
        for day in range(days):
            if day:
                date = world.call("next_day")
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
            (run_dir / "records.json").write_text(
                json.dumps(world.call("records"), indent=1, default=str)
            )
            (run_dir / "notepads.json").write_text(json.dumps(notepads, indent=1))
    except WorldError as error:
        bump("crashes")
        summary["status"] = "stopped: the world's code crashed"
        log.write({"type": "crash", "error": str(error)})
        print(f"stopped: {str(error).strip().splitlines()[-1]}", flush=True)
    finally:
        world.close()
        (run_dir / "notepads.json").write_text(json.dumps(notepads, indent=1))
    return {**summary, **counts}
