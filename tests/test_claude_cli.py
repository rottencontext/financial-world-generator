"""The Claude Code CLI backend, with a fake `claude` instead of the real one."""

import json
import subprocess
from typing import Any

import pytest

from worldgen import claude_cli
from worldgen.claude_cli import chat
from worldgen.llm import LlmError

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bank_transfer",
            "description": "Move money.",
            "parameters": {"type": "object", "properties": {"amount": {"type": "string"}}},
        },
    }
]


class FakeClaude:
    """Records each `claude -p` command and answers with the next canned result."""

    def __init__(self, results: list[dict[str, Any]]):
        self.results = results
        self.calls: list[tuple[dict[str, str | None], str]] = []
        self.envs: list[dict[str, str]] = []

    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        options: dict[str, str | None] = {}
        for index, part in enumerate(command):
            if part.startswith("--"):
                following = command[index + 1] if index + 1 < len(command) else None
                options[part] = (
                    None if following is None or following.startswith("--") else following
                )
        self.calls.append((options, kwargs["input"]))
        self.envs.append(kwargs["env"])
        answer = self.results.pop(0)  # a list of stream events, or just the result event
        events = answer if isinstance(answer, list) else [{"type": "result", **answer}]
        stdout = "\n".join(json.dumps(event) for event in events)
        return subprocess.CompletedProcess(command, 0, stdout, "")


def result(**fields: Any) -> dict[str, Any]:
    return {
        "is_error": False,
        "subtype": "success",
        "session_id": "s1",
        "total_cost_usd": 0.5,
        **fields,
    }


@pytest.fixture(autouse=True)
def clear_sessions() -> None:
    claude_cli._sessions.clear()


def test_tool_calls_go_through_the_json_schema_and_come_back_openai_style(monkeypatch: Any) -> None:
    fake = FakeClaude(
        [
            result(
                structured_output={
                    "content": "Payroll needs funding.",
                    "tool_calls": [{"name": "bank_transfer", "arguments": {"amount": "60.00"}}],
                },
                usage={"input_tokens": 10, "output_tokens": 5},
            )
        ]
    )
    monkeypatch.setattr(subprocess, "run", fake)
    messages = [
        {"role": "system", "content": "You are Sam."},
        {"role": "user", "content": "Today is Monday."},
    ]

    reply, usage = chat("sonnet", messages, TOOLS, effort="low")

    options, prompt = fake.calls[0]
    assert options["--model"] == "sonnet" and options["--effort"] == "low"
    assert options["--tools"] == "" and "--strict-mcp-config" in options
    system = options["--system-prompt"] or ""
    assert system.startswith("You are Sam.") and "bank_transfer" in system
    assert json.loads(options["--json-schema"] or "")["properties"]["tool_calls"]["items"][
        "properties"
    ]["name"]["enum"] == ["bank_transfer"]
    assert "## user\nToday is Monday." in prompt and "--resume" not in options
    assert reply["content"] == "Payroll needs funding."
    call = reply["tool_calls"][0]
    assert call["function"] == {"name": "bank_transfer", "arguments": '{"amount": "60.00"}'}
    assert call["id"].startswith("call_bank_transfer_")
    assert usage["cost"] == 0.5 and usage["finish_reason"] == "tool_calls"
    assert usage["input_tokens"] == 10 and usage["session_id"] == "s1"


def test_tool_results_resume_the_session_and_cost_the_difference(monkeypatch: Any) -> None:
    fake = FakeClaude(
        [
            result(
                structured_output={
                    "content": "Funding.",
                    "tool_calls": [{"name": "bank_transfer", "arguments": {"amount": "60.00"}}],
                }
            ),
            result(
                structured_output={"content": "Done for today.", "tool_calls": []},
                total_cost_usd=0.8,
            ),
        ]
    )
    monkeypatch.setattr(subprocess, "run", fake)
    messages = [
        {"role": "system", "content": "You are Sam."},
        {"role": "user", "content": "Today."},
    ]

    reply, _ = chat("sonnet", messages, TOOLS)
    messages.append(reply)
    messages.append(
        {"role": "tool", "tool_call_id": reply["tool_calls"][0]["id"], "content": "Moved $60."}
    )
    reply, usage = chat("sonnet", messages, TOOLS)

    options, prompt = fake.calls[1]
    assert options["--resume"] == "s1"
    assert (
        prompt.startswith("## result of tool call call_bank_transfer_") and "Moved $60." in prompt
    )
    assert "Today." not in prompt  # the session already has it
    assert reply == {"role": "assistant", "content": "Done for today."}
    assert usage["cost"] == pytest.approx(0.3) and usage["finish_reason"] == "stop"


def test_a_changed_transcript_starts_a_fresh_session(monkeypatch: Any) -> None:
    fake = FakeClaude(
        [
            result(structured_output={"content": "a", "tool_calls": []}),
            result(structured_output={"content": "b", "tool_calls": []}, session_id="s2"),
        ]
    )
    monkeypatch.setattr(subprocess, "run", fake)
    messages = [{"role": "system", "content": "S"}, {"role": "user", "content": "one"}]
    chat("sonnet", messages, TOOLS)
    messages[-1] = {"role": "user", "content": "changed"}
    messages.append({"role": "user", "content": "two"})
    chat("sonnet", messages, TOOLS)

    options, prompt = fake.calls[1]
    assert "--resume" not in options and "## user\nchanged" in prompt and "## user\ntwo" in prompt


def test_without_tools_the_text_result_is_the_reply(monkeypatch: Any) -> None:
    fake = FakeClaude([result(result="<world.py>\nx = 1\n</world.py>")])
    monkeypatch.setattr(subprocess, "run", fake)

    reply, usage = chat("opus", [{"role": "user", "content": "Write a world."}], effort="medium")

    options, prompt = fake.calls[0]
    assert "--json-schema" not in options and "--no-session-persistence" in options
    assert options["--effort"] == "medium" and prompt.endswith("## assistant\n")
    assert reply == {"role": "assistant", "content": "<world.py>\nx = 1\n</world.py>"}
    assert usage["finish_reason"] == "stop"


def test_the_output_cap_is_raised_to_max_tokens(monkeypatch: Any) -> None:
    fake = FakeClaude([result(result="ok")])
    monkeypatch.setattr(subprocess, "run", fake)

    chat("fable", [{"role": "user", "content": "Write a world."}])

    assert fake.envs[0]["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] == "128000"


def test_a_reply_continued_past_the_output_cap_comes_back_whole(monkeypatch: Any) -> None:
    # Claude Code continues a capped reply in new turns; its `result` holds only the last part.
    def said(message_id: str, text: str) -> dict[str, Any]:
        content = [{"type": "text", "text": text}]
        return {"type": "assistant", "message": {"id": message_id, "content": content}}

    fake = FakeClaude(
        [
            [
                {"type": "system", "subtype": "init"},
                {"type": "assistant", "message": {"id": "m1", "content": [{"type": "thinking"}]}},
                said("m1", "<world.py>\nx = 1\ny ="),
                {"type": "user", "message": {"content": "Output token limit hit. Resume directly"}},
                said("m2", "y = 2\nz = 3\n"),
                said("m3", "</world.py>"),
                {"type": "result", **result(result="</world.py>", num_turns=3)},
            ]
        ]
    )
    monkeypatch.setattr(subprocess, "run", fake)

    reply, usage = chat("fable", [{"role": "user", "content": "Write a world."}])

    assert reply["content"] == "<world.py>\nx = 1\ny = 2\nz = 3\n</world.py>"
    assert usage["finish_reason"] == "stop"


def test_when_claude_gives_up_continuing_the_parts_come_back_as_cut_off(monkeypatch: Any) -> None:
    text = {"type": "text", "text": "x"}
    said = {"type": "assistant", "message": {"id": "m1", "content": [text]}}
    error = "API Error: Claude's response exceeded the 400 output token maximum."
    # The CLI also prints the error as a synthetic assistant message; it is not part of the reply.
    synthetic = {
        "type": "assistant",
        "is_api_error_message": True,
        "message": {"id": "e1", "model": "<synthetic>", "content": [{**text, "text": error}]},
    }
    final = {"type": "result", **result(result=error, is_error=True)}
    fake = FakeClaude([[said, synthetic, final]])
    monkeypatch.setattr(subprocess, "run", fake)

    reply, usage = chat("fable", [{"role": "user", "content": "Write a world."}])

    assert reply["content"] == "x" and usage["finish_reason"] == "length"


def test_tool_choice_none_offers_no_tools(monkeypatch: Any) -> None:
    fake = FakeClaude([result(result="Finished.")])
    monkeypatch.setattr(subprocess, "run", fake)

    reply, _ = chat(
        "sonnet", [{"role": "user", "content": "No more calls."}], TOOLS, tool_choice="none"
    )

    options, _ = fake.calls[0]
    assert "--json-schema" not in options and reply["content"] == "Finished."


def test_claude_errors_become_llm_errors(monkeypatch: Any) -> None:
    fake = FakeClaude(
        [{"is_error": True, "subtype": "error", "result": "You've hit your usage limit"}]
    )
    monkeypatch.setattr(subprocess, "run", fake)

    with pytest.raises(LlmError, match="usage limit"):
        chat("sonnet", [{"role": "user", "content": "hi"}], TOOLS)


def test_a_failed_resume_falls_back_to_the_whole_transcript(monkeypatch: Any) -> None:
    fake = FakeClaude(
        [
            result(structured_output={"content": "a", "tool_calls": []}),
            {"is_error": True, "subtype": "error", "result": "No conversation found"},
            result(structured_output={"content": "b", "tool_calls": []}, session_id="s3"),
        ]
    )
    monkeypatch.setattr(subprocess, "run", fake)
    messages = [{"role": "system", "content": "S"}, {"role": "user", "content": "one"}]
    reply, _ = chat("sonnet", messages, TOOLS)
    messages += [reply, {"role": "user", "content": "two"}]

    reply, _ = chat("sonnet", messages, TOOLS)

    assert reply["content"] == "b"
    assert fake.calls[1][0]["--resume"] == "s1"
    options, prompt = fake.calls[2]
    assert "--resume" not in options and "## user\none" in prompt and "## assistant\na" in prompt
