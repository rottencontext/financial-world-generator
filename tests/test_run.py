"""The runner end to end on a hand-written world, with a fake model instead of an LLM."""

import json
from pathlib import Path
from typing import Any

from worldgen.generate import generate
from worldgen.log import RunLog
from worldgen.simulate import simulate

WORLD = """
from datetime import date, timedelta
from decimal import Decimal

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

def call_tool(agent, name, args):
    amount = Decimal(args["amount"])
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
    today += timedelta(days=1)
    return today.isoformat()

def records():
    return {"bank": {"postings": postings}}
"""

PROMPTS = {
    "agents": {"sam": {"entity": "company", "prompt": "You are Sam.", "notepad": "Fund payroll."}}
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


def done(notepad: str) -> dict[str, Any]:
    return {"role": "assistant", "content": notepad}


def generated_reply() -> dict[str, Any]:
    content = (
        f"<world.py>\n{WORLD}</world.py>\n<prompts.json>\n{json.dumps(PROMPTS)}\n</prompts.json>"
    )
    return {"role": "assistant", "content": content}


def test_generate_writes_files_and_dry_runs(tmp_path: Path) -> None:
    log = RunLog(tmp_path / "log.jsonl")
    assert generate("A tiny company.", tmp_path, 3, "m", log, llm=fake_llm([generated_reply()]))
    assert json.loads((tmp_path / "prompts.json").read_text()) == PROMPTS


def test_generate_strips_markdown_fences_inside_tags(tmp_path: Path) -> None:
    fenced = {
        "role": "assistant",
        "content": f"<world.py>\n```python   \n{WORLD}```  \n</world.py>\n"
        f"<prompts.json>\n```json \n{json.dumps(PROMPTS)}\n```\n</prompts.json>",
    }
    log = RunLog(tmp_path / "log.jsonl")
    assert generate("A tiny company.", tmp_path, 3, "m", log, llm=fake_llm([fenced]))
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
    assert generate("A tiny company.", tmp_path, 3, "m", log, llm=llm)
    events = [json.loads(line) for line in (tmp_path / "log.jsonl").read_text().splitlines()]
    assert "boom" in events[0]["problem"] and events[1]["problem"] is None


def test_generate_catches_non_dict_prompts_json(tmp_path: Path) -> None:
    bad_json = {
        "role": "assistant",
        "content": f"<world.py>\n{WORLD}</world.py>\n<prompts.json>\n[1, 2, 3]\n</prompts.json>",
    }
    log = RunLog(tmp_path / "log.jsonl")
    llm = fake_llm([bad_json, generated_reply()])
    assert generate("A tiny company.", tmp_path, 3, "m", log, llm=llm)
    events = [json.loads(line) for line in (tmp_path / "log.jsonl").read_text().splitlines()]
    assert "prompts.json" in events[0]["problem"] and events[1]["problem"] is None


def test_simulate_logs_calls_rejections_and_records(tmp_path: Path) -> None:
    (tmp_path / "world.py").write_text(WORLD)
    (tmp_path / "prompts.json").write_text(json.dumps(PROMPTS))
    log = RunLog(tmp_path / "log.jsonl")
    # Day 1 (Friday): move $60. Days 2-3: weekend, nobody acts. Day 4: try $60 more.
    replies = [tool_call("60.00"), done("Moved 60."), tool_call("60.00"), done("Short by 20.")]
    summary = simulate(tmp_path, 4, "m", log, llm=fake_llm(replies))
    log.close()

    assert summary["status"] == "finished" and summary["calls"] == 2 and summary["turns"] == 2
    calls = [json.loads(line) for line in (tmp_path / "log.jsonl").read_text().splitlines()]
    calls = [event for event in calls if event["type"] == "call"]
    assert calls[0]["result"] == "Moved $60.00." and calls[0]["entity"] == "bank"
    assert calls[1]["result"] == "Rejected: ops holds $40.00, transfer needs $60.00."
    assert calls[0]["why"] == "Payroll needs funding."
    records = json.loads((tmp_path / "records.json").read_text())
    assert records == {"bank": {"postings": [{"date": "2021-01-01", "amount": "60.00"}]}}
    assert json.loads((tmp_path / "notepads.json").read_text()) == {"sam": "Short by 20."}
    assert round(log.cost_usd, 2) == 0.04


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
    replies = [tool_call("60.00"), done("Moved 60 on day 1.")]
    summary = simulate(tmp_path, 2, "m", log, llm=fake_llm(replies))
    log.close()

    assert summary["status"] == "stopped: the world's code crashed"
    assert summary["crashes"] == 1
    assert summary["last_date"] == "2021-01-01"
    records = json.loads((tmp_path / "records.json").read_text())
    assert records == {"bank": {"postings": [{"date": "2021-01-01", "amount": "60.00"}]}}
    assert json.loads((tmp_path / "notepads.json").read_text()) == {"sam": "Moved 60 on day 1."}
