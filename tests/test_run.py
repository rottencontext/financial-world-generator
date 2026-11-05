"""The runner end to end on a hand-written world, with a fake model instead of an LLM."""

import json
from pathlib import Path
from typing import Any

import pytest

from worldgen import generate as generate_module
from worldgen import simulate as simulate_module
from worldgen.generate import dry_run, generate
from worldgen.log import RunLog
from worldgen.simulate import simulate

WORLD = """
from datetime import date, timedelta
from decimal import Decimal

END = date(2021, 1, 4)  # the main prompt's last day: Friday to Monday
today = None
balances = {}
postings = []

def start():
    global today
    today = date(2021, 1, 1)
    balances.update(ops=Decimal("100.00"), payroll=Decimal("0.00"))
    return today.isoformat()

def agents_today():
    return ["sam"] if today.weekday() < 5 else []

def tools(agent):
    return [{"name": "bank_transfer", "entity": "bank", "description": "Move money.",
             "input_schema": {"type": "object", "properties": {"amount": {"type": "string"}}}}]

def money(x):
    try:
        return Decimal(str(x).replace("$", "").replace(",", "").strip())
    except Exception:
        return None

def call_tool(agent, name, args):
    amount = money(args.get("amount"))
    if amount is None or amount <= 0:
        return "Give the amount in dollars, e.g. 60.00."
    if amount > balances["ops"]:
        return f"Rejected: ops holds ${balances['ops']}, transfer needs ${amount}."
    balances["ops"] -= amount
    balances["payroll"] += amount
    postings.append({"date": today.isoformat(), "amount": amount})
    return f"Moved ${amount}."

def status(agent):
    return f"ops ${balances['ops']}, payroll ${balances['payroll']}"

def next_day():
    global today
    if today == END:
        return None
    today += timedelta(days=1)
    return today.isoformat()

def records():
    return {"bank": {"postings": postings}}
"""

PROMPTS = {
    "agents": {
        "sam": {
            "entity": "company",
            "prompt": "You are Sam.",
            "plans": [{"due": "2021-01-01", "task": "Fund payroll."}],
        }
    }
}


def fake_llm(replies: list[Any]) -> Any:
    def llm(model: str, messages: list[Any], tools: Any = None, **_: Any) -> Any:
        return replies.pop(0), {"cost": 0.01}

    return llm


def tool_call(amount: str) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": "Payroll needs funding.",
        "tool_calls": [
            {
                "id": "c1",
                "type": "function",
                "function": {"name": "bank_transfer", "arguments": json.dumps({"amount": amount})},
            }
        ],
    }


def memory_call(**args: Any) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": "Updating memory.",
        "tool_calls": [
            {
                "id": "m1",
                "type": "function",
                "function": {"name": "memory", "arguments": json.dumps(args)},
            }
        ],
    }


def done(reply: str) -> dict[str, Any]:
    return {"role": "assistant", "content": reply}


def generated_reply() -> dict[str, Any]:
    content = (
        f"<world.py>\n{WORLD}</world.py>\n<prompts.json>\n{json.dumps(PROMPTS)}\n</prompts.json>"
    )
    return {"role": "assistant", "content": content}


def test_generate_writes_files_and_dry_runs(tmp_path: Path) -> None:
    log = RunLog(tmp_path / "log.jsonl")
    assert generate("A tiny company.", tmp_path, "m", log, llm=fake_llm([generated_reply()]))
    assert json.loads((tmp_path / "prompts.json").read_text()) == PROMPTS


def test_generate_strips_markdown_fences_inside_tags(tmp_path: Path) -> None:
    fenced = {
        "role": "assistant",
        "content": f"<world.py>\n```python   \n{WORLD}```  \n</world.py>\n"
        f"<prompts.json>\n```json \n{json.dumps(PROMPTS)}\n```\n</prompts.json>",
    }
    log = RunLog(tmp_path / "log.jsonl")
    assert generate("A tiny company.", tmp_path, "m", log, llm=fake_llm([fenced]))
    assert not (tmp_path / "world.py").read_text().lstrip().startswith("```")


def test_generate_sends_crash_back_for_a_fix(tmp_path: Path) -> None:
    broken = {
        "role": "assistant",
        "content": generated_reply()["content"].replace(
            "def next_day():", "def next_day():\n    raise RuntimeError('boom')\n\ndef _old():"
        ),
    }
    log = RunLog(tmp_path / "log.jsonl")
    llm = fake_llm([broken, generated_reply()])
    assert generate("A tiny company.", tmp_path, "m", log, llm=llm)
    events = [json.loads(line) for line in (tmp_path / "log.jsonl").read_text().splitlines()]
    assert "boom" in events[0]["problem"] and events[1]["problem"] is None


def test_generate_catches_non_dict_prompts_json(tmp_path: Path) -> None:
    bad_json = {
        "role": "assistant",
        "content": f"<world.py>\n{WORLD}</world.py>\n<prompts.json>\n[1, 2, 3]\n</prompts.json>",
    }
    log = RunLog(tmp_path / "log.jsonl")
    llm = fake_llm([bad_json, generated_reply()])
    assert generate("A tiny company.", tmp_path, "m", log, llm=llm)
    events = [json.loads(line) for line in (tmp_path / "log.jsonl").read_text().splitlines()]
    assert "prompts.json" in events[0]["problem"] and events[1]["problem"] is None


def test_dry_run_rejects_world_tool_named_memory(tmp_path: Path) -> None:
    collision = WORLD.replace('"bank_transfer"', '"memory"')
    write_world(tmp_path, collision)
    problem = dry_run(tmp_path)
    assert problem and "'memory' is reserved" in problem


def test_simulate_logs_calls_rejections_and_records(tmp_path: Path) -> None:
    (tmp_path / "world.py").write_text(WORLD)
    (tmp_path / "prompts.json").write_text(json.dumps(PROMPTS))
    log = RunLog(tmp_path / "log.jsonl")
    # Day 1 (Friday): move $60. Days 2-3: weekend, nobody acts. Day 4, the last: try $60 more,
    # then record a note via the memory tool. Plain end-of-turn replies go only to the log.
    replies = [
        tool_call("60.00"),
        done("Moved 60."),
        tool_call("60.00"),
        memory_call(action="add_note", text="Short by 20."),
        done("Done for Monday."),
    ]
    summary = simulate(tmp_path, "m", log, llm=fake_llm(replies))
    log.close()

    assert summary["status"] == "finished" and summary["calls"] == 3 and summary["turns"] == 2
    assert summary["first_date"] == "2021-01-01" and summary["last_date"] == "2021-01-04"
    events = [json.loads(line) for line in (tmp_path / "log.jsonl").read_text().splitlines()]
    assert len([event for event in events if event["type"] == "day"]) == 4
    calls = [event for event in events if event["type"] == "call"]
    assert calls[0]["result"] == "Moved $60.00." and calls[0]["entity"] == "bank"
    assert calls[1]["result"] == "Rejected: ops holds $40.00, transfer needs $60.00."
    assert calls[2]["tool"] == "memory" and calls[2]["entity"] == "runner"
    assert calls[2]["result"] == "Added note n1 (2021-01-04): Short by 20."
    assert calls[0]["why"] == "Payroll needs funding."
    turns = [event for event in events if event["type"] == "turn"]
    assert turns[0]["reply"] == "Moved 60."
    assert turns[1]["reply"] == "Done for Monday."
    records = json.loads((tmp_path / "records.json").read_text())
    assert records == {"bank": {"postings": [{"date": "2021-01-01", "amount": "60.00"}]}}
    # The dated plan p1 stayed across the quiet/failed turns because Sam never marked it done,
    # and the note carries the date it was added (2021-01-04).
    assert json.loads((tmp_path / "notepads.json").read_text()) == {
        "sam": {
            "plans": [{"id": "p1", "due": "2021-01-01", "task": "Fund payroll."}],
            "notes": [{"id": "n1", "date": "2021-01-04", "text": "Short by 20."}],
        }
    }
    assert round(log.cost_usd, 2) == 0.05


def test_memory_keeps_plans_until_done_and_dates_every_note(tmp_path: Path) -> None:
    write_world(tmp_path, WORLD)
    log = RunLog(tmp_path / "log.jsonl")
    captured_prompts: list[str] = []

    script = [
        # Day 1 (2021-01-01): add a note about a holiday/observation and a future plan for Jan 4;
        # reply at end of turn without touching p1.
        memory_call(action="add_note", text="2021-01-01: bank holiday observation"),
        memory_call(action="add_plan", due="2021-01-04", text="Finish funding payroll."),
        done("Quiet Friday reply that must not overwrite plans."),
        # Day 4 (2021-01-04): mark p1 done, replace n1 with a new observation, and finish.
        memory_call(action="done_plan", id="p1"),
        memory_call(action="replace_note", id="n1", text="Ops balance checked."),
        done("All caught up."),
    ]

    def capturing_llm(model: str, messages: list[Any], tools: Any = None, **_: Any) -> Any:
        if len(messages) == 2:
            captured_prompts.append(messages[1]["content"])
        return script.pop(0), {"cost": 0.01}

    simulate(tmp_path, "m", log, llm=capturing_llm)
    log.close()

    # On Day 4 (2021-01-04), the user prompt shows both plans (p1 and p2) marked [DUE]
    # and the Day 1 note stamped with 2021-01-01 (without double-stamping the date).
    day4_prompt = captured_prompts[1]
    assert "- [p1] 2021-01-01 [DUE]: Fund payroll." in day4_prompt
    assert "- [p2] 2021-01-04 [DUE]: Finish funding payroll." in day4_prompt
    assert "- [n1] 2021-01-01: bank holiday observation" in day4_prompt
    assert "Quiet Friday reply" not in day4_prompt

    assert json.loads((tmp_path / "notepads.json").read_text()) == {
        "sam": {
            "plans": [{"id": "p2", "due": "2021-01-04", "task": "Finish funding payroll."}],
            "notes": [{"id": "n1", "date": "2021-01-04", "text": "Ops balance checked."}],
        }
    }


def test_simulate_saves_records_each_day_before_later_crash(tmp_path: Path) -> None:
    crashing_world = WORLD.replace(
        "today += timedelta(days=1)",
        "today += timedelta(days=1)\n"
        "    if today.day == 2:\n"
        "        raise RuntimeError('day 2 crash')",
    )
    (tmp_path / "world.py").write_text(crashing_world)
    (tmp_path / "prompts.json").write_text(json.dumps(PROMPTS))
    log = RunLog(tmp_path / "log.jsonl")
    replies = [
        tool_call("60.00"),
        memory_call(action="add_note", text="Moved 60 on day 1."),
        done("Turn finished."),
    ]
    summary = simulate(tmp_path, "m", log, llm=fake_llm(replies))
    log.close()

    assert summary["status"] == "stopped: the world's code crashed"
    assert summary["crashes"] == 1
    assert summary["last_date"] == "2021-01-01"
    records = json.loads((tmp_path / "records.json").read_text())
    assert records == {"bank": {"postings": [{"date": "2021-01-01", "amount": "60.00"}]}}
    assert json.loads((tmp_path / "notepads.json").read_text()) == {
        "sam": {
            "plans": [{"id": "p1", "due": "2021-01-01", "task": "Fund payroll."}],
            "notes": [{"id": "n1", "date": "2021-01-01", "text": "Moved 60 on day 1."}],
        }
    }


FRAGILE_MONEY = WORLD.replace(
    'amount = money(args.get("amount"))', 'amount = Decimal(args["amount"])'
)

# A request tool for sam and a review tool for a clerk who acts only while a request is pending,
# so the dry run must carry the id "REQ-1" from sam's result to the clerk's call.
TWO_AGENTS = (
    WORLD.replace('return ["sam"] if', 'return ["sam"] + (["clerk"] if pending else []) if')
    .replace("postings = []", "postings = []\npending = []")
    .replace(
        "def tools(agent):",
        "def tools(agent):\n"
        "    if agent == 'clerk':\n"
        "        return [{'name': 'approve', 'entity': 'bank', 'description': 'Approve.',\n"
        "                 'input_schema': {'type': 'object', 'properties': {\n"
        "                     'request_id': {'type': 'string'}, 'amount': {'type': 'string'}}}}]\n"
        "    return tools_sam()\n\n"
        "def tools_sam():",
    )
    .replace(
        "def call_tool(agent, name, args):",
        "def call_tool(agent, name, args):\n"
        "    if name == 'approve':\n"
        "        if args.get('request_id') not in pending:\n"
        "            return 'No such request.'\n"
        "        pending.remove(args['request_id'])\n"
        "        return 'Approved ' + str(Decimal(args['amount']))\n"
        "    if not pending:\n"
        "        pending.append('REQ-1')\n"
        "        return 'Request REQ-1 filed.'\n"
        "    return call_sam(agent, name, args)\n\n"
        "def call_sam(agent, name, args):",
    )
)


def write_world(tmp_path: Path, world: str, prompts: dict[str, Any] = PROMPTS) -> None:
    (tmp_path / "world.py").write_text(world)
    (tmp_path / "prompts.json").write_text(json.dumps(prompts))


def test_dry_run_passes_a_world_that_rejects_messy_arguments(tmp_path: Path) -> None:
    write_world(tmp_path, WORLD)
    assert dry_run(tmp_path) is None


def test_dry_run_calls_tools_with_messy_amounts(tmp_path: Path) -> None:
    write_world(tmp_path, FRAGILE_MONEY)
    problem = dry_run(tmp_path)
    assert problem and "call_tool('sam', 'bank_transfer'" in problem
    assert "decimal.InvalidOperation" in problem


def test_dry_run_runs_next_day_after_tools_queue_items(tmp_path: Path) -> None:
    # A transfer queues a string date that the nightly code compares with a date.
    world = WORLD.replace(
        'postings.append({"date": today.isoformat(), "amount": amount})',
        'postings.append({"date": today.isoformat(), "amount": amount})\n'
        "    queued.append(today.isoformat())",
    ).replace(
        "today += timedelta(days=1)",
        "[q for q in queued if q <= today]\n    today += timedelta(days=1)",
    )
    write_world(tmp_path, world.replace("postings = []", "postings = []\nqueued = []"))
    problem = dry_run(tmp_path)
    assert problem and problem.startswith("The dry run crashed in next_day()")
    assert "TypeError" in problem


def test_dry_run_carries_ids_from_results_to_other_agents(tmp_path: Path) -> None:
    prompts = {"agents": {**PROMPTS["agents"], "clerk": {"entity": "bank", "prompt": "Clerk."}}}
    write_world(tmp_path, TWO_AGENTS, prompts)
    # Friday: sam files REQ-1. The clerk's first weekday is Monday, day 4.
    problem = dry_run(tmp_path)
    assert problem and "call_tool('clerk', 'approve'" in problem and '"REQ-1"' in problem


def test_simulate_shows_the_crash_reason_to_the_agent(tmp_path: Path) -> None:
    write_world(tmp_path, FRAGILE_MONEY)
    log = RunLog(tmp_path / "log.jsonl")
    replies = [tool_call("$60.00"), done("Odd."), done("Nothing today.")]
    summary = simulate(tmp_path, "m", log, llm=fake_llm(replies))
    log.close()
    assert summary["crashes"] == 1
    events = [json.loads(line) for line in (tmp_path / "log.jsonl").read_text().splitlines()]
    call = next(event for event in events if event["type"] == "call")
    assert call["result"].startswith("Error: the world's code crashed on this call:")
    assert "decimal.InvalidOperation" in call["result"]


NEVER_ENDS = WORLD.replace("    if today == END:\n        return None\n", "")


def test_dry_run_fails_a_world_that_never_ends(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generate_module, "MAX_DAYS", 10)
    write_world(tmp_path, NEVER_ENDS)
    problem = dry_run(tmp_path)
    assert problem and problem.startswith("next_day() still returned a date after 10 days")


def test_simulate_stops_a_world_that_never_ends(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(simulate_module, "MAX_DAYS", 3)  # Friday to Sunday: nobody acts
    write_world(tmp_path, NEVER_ENDS)
    log = RunLog(tmp_path / "log.jsonl")
    summary = simulate(tmp_path, "m", log, llm=fake_llm([]))
    log.close()
    assert summary["status"] == "stopped: the world's code crashed"
    assert summary["last_date"] == "2021-01-03"
