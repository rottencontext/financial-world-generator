"""One model call through the Claude Code CLI, so whatever `claude` is logged in as pays for
the run: a Claude Pro or Max subscription, or an API key.

Each call runs `claude -p` with the conversation rendered as text, Claude Code's own tools
turned off and, when tools are offered, a JSON schema that carries the reply: text plus the
tool calls the model wants. Tool results go back as the next prompt of the same Claude Code
session (`--resume`), so the transcript is sent once and stays cached. API keys in the
environment are dropped so the login is what pays.

Claude Code caps each reply at CLAUDE_CODE_MAX_OUTPUT_TOKENS (64000 for Fable unless raised;
here it is MAX_TOKENS) and continues a capped reply in further turns, while its `result` keeps
only the last one. So the output is read as a stream and the parts are joined. The CLI gives up
after three continuations; what came through is then returned as cut off (finish_reason
"length") so the caller can ask for something shorter.

Docs: https://code.claude.com/docs/en/headless
"""

import copy
import json
import os
import re
import subprocess
import tempfile
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from worldgen.llm import MAX_TOKENS, LlmError, Message

TIMEOUT = 1800  # a reply near MAX_TOKENS takes about half an hour
MAX_SESSIONS = 64
DROPPED_ENV = {"CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"}
CUT_OFF = re.compile(r"exceeded the \d+ output token maximum")
USAGE_KEYS = (
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
)

PROTOCOL = """\
## How you act
You cannot invoke tools yourself in this environment, so never try to call one; the only \
function wired up here is the one that returns your JSON reply. Names in the tool list below \
are not functions you can call, and calling one fails. Your reply is a JSON object with two \
fields:
- "content": what you say: one sentence on why before any tool call, or your final reply. \
null when there is nothing to say.
- "tool_calls": the tools you want run now, in order, each as {"name", "arguments"} with \
arguments matching the tool's parameters. The runner executes them after your reply and \
sends each result back in the next message, labeled with the tool's name. Leave the list \
empty when you are done.

## Tools the runner can execute for you
"""


@dataclass
class _Session:
    session_id: str
    prefix: list[Message]  # what the Claude Code session has already seen
    cost_usd: float  # the conversation total claude reported last time


_sessions: dict[int, _Session] = {}
_lock = threading.Lock()


def chat(
    model: str,
    messages: list[Message],
    tools: list[dict[str, Any]] | None = None,
    effort: str = "low",
    tool_choice: str | None = None,
) -> tuple[Message, dict[str, Any]]:
    """Return the assistant message (kept verbatim for the next call) and the usage."""
    offered = [tool["function"] for tool in tools or []] if tool_choice != "none" else []
    session = _resumable(messages)
    try:
        return _call(model, messages, offered, effort, session)
    except LlmError:
        if session is None:
            raise
        with _lock:  # the session could not be resumed: send the whole transcript again
            _sessions.pop(id(messages), None)
        return _call(model, messages, offered, effort, None)


def _call(
    model: str,
    messages: list[Message],
    offered: list[dict[str, Any]],
    effort: str,
    session: _Session | None,
) -> tuple[Message, dict[str, Any]]:
    system = "\n\n".join(str(m.get("content") or "") for m in messages if m["role"] == "system")
    if offered:
        system += "\n\n" + PROTOCOL + json.dumps(offered, indent=1)
    new = messages[len(session.prefix) :] if session else messages
    prompt = _render(new) + "\n\n## assistant\n" + ("Reply as JSON." if offered else "")
    command = [
        "claude",
        "-p",
        "--model",
        model,
        "--effort",
        effort,
        "--system-prompt",
        system,
        "--tools",
        "",
        "--strict-mcp-config",
        "--no-chrome",
        "--disable-slash-commands",
        "--permission-mode",
        "dontAsk",
        "--permission-prompts",
        "none",
        "--max-turns",
        "4",
        "--output-format",
        "stream-json",
        "--verbose",  # stream-json needs it
    ]
    if offered:
        command += ["--json-schema", json.dumps(_schema([tool["name"] for tool in offered]))]
    if session:
        command += ["--resume", session.session_id]
    elif not offered:
        command += ["--no-session-persistence"]
    data = _run(command, prompt)
    cut_off = bool(data.get("joined") and not offered and CUT_OFF.search(str(data.get("result"))))
    if (data.get("is_error") and not cut_off) or data.get("subtype") != "success":
        raise LlmError(f"claude ({data.get('subtype')}): {str(data.get('result'))[:500]}")
    reply = _reply(data, offered)
    total = float(data.get("total_cost_usd") or 0)
    raw_usage = data.get("usage") or {}
    usage: dict[str, Any] = {key: raw_usage.get(key) for key in USAGE_KEYS}
    usage.update(
        cost=total - (session.cost_usd if session else 0.0),
        cost_basis="list price; a subscription is not billed per call",
        finish_reason="length" if cut_off else "tool_calls" if reply.get("tool_calls") else "stop",
        session_id=data.get("session_id"),
    )
    if offered or session:
        _remember(messages, reply, str(data.get("session_id") or ""), total)
    return reply, usage


def _render(messages: list[Message]) -> str:
    parts = []
    for message in messages:
        role = message.get("role")
        if role == "assistant":
            lines = [str(message["content"])] if message.get("content") else []
            for call in message.get("tool_calls") or []:
                fn = call.get("function") or {}
                lines.append(
                    f"[tool call {call.get('id')}: {fn.get('name')} {fn.get('arguments')}]"
                )
            parts.append("## assistant\n" + "\n".join(lines))
        elif role == "tool":
            parts.append(
                f"## result of tool call {message.get('tool_call_id')}\n{message.get('content')}"
            )
        elif role == "user":
            parts.append(f"## user\n{message.get('content')}")
    return "\n\n".join(parts)


def _schema(names: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "content": {"type": ["string", "null"]},
            "tool_calls": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "enum": names},
                        "arguments": {"type": "object"},
                    },
                    "required": ["name", "arguments"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["content", "tool_calls"],
        "additionalProperties": False,
    }


def _reply(data: dict[str, Any], offered: list[dict[str, Any]]) -> Message:
    if not offered:
        return {"role": "assistant", "content": str(data.get("joined") or data.get("result") or "")}
    out = data.get("structured_output")
    if not isinstance(out, dict):
        raise LlmError(f"claude returned no structured reply: {str(data.get('result'))[:300]}")
    reply: Message = {"role": "assistant", "content": out.get("content")}
    calls = [
        {
            # The id names the tool, so the result's label does too.
            "id": f"call_{call['name']}_{uuid.uuid4().hex[:6]}",
            "type": "function",
            "function": {
                "name": call["name"],
                "arguments": json.dumps(call.get("arguments") or {}),
            },
        }
        for call in out.get("tool_calls") or []
        if isinstance(call, dict) and call.get("name")
    ]
    if calls:
        reply["tool_calls"] = calls
    return reply


def _run(command: list[str], prompt: str) -> dict[str, Any]:
    env = {key: value for key, value in os.environ.items() if key not in DROPPED_ENV}
    env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(MAX_TOKENS)  # the CLI clamps it per model
    cwd = Path(tempfile.gettempdir()) / "worldgen-claude"  # keeps the sessions out of your projects
    cwd.mkdir(exist_ok=True)
    try:
        done = subprocess.run(
            command, input=prompt, capture_output=True, text=True, timeout=TIMEOUT, env=env, cwd=cwd
        )
    except FileNotFoundError as error:
        raise LlmError("claude is not installed: https://code.claude.com/docs/en/setup") from error
    except subprocess.TimeoutExpired as error:
        raise LlmError(f"claude gave no answer in {TIMEOUT}s") from error
    events = []
    for line in done.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict):
            events.append(event)
    results = [event for event in events if event.get("type") == "result"]
    if not results:
        raise LlmError(f"claude exit {done.returncode}: {(done.stderr or done.stdout)[:500]}")
    data = results[-1]
    data["joined"] = _join(_text_parts(events))
    return data


def _text_parts(events: list[dict[str, Any]]) -> list[str]:
    """The text of each assistant message, in order. A message can span several events."""
    parts: dict[str, str] = {}
    for event in events:
        message = event.get("message") or {}
        if event.get("is_api_error_message") or message.get("model") == "<synthetic>":
            continue  # the CLI's own error text, dressed up as an assistant message
        if event.get("type") == "assistant" and isinstance(message.get("content"), list):
            text = "".join(
                str(block.get("text") or "")
                for block in message["content"]
                if isinstance(block, dict) and block.get("type") == "text"
            )
            key = str(message.get("id") or len(parts))
            parts[key] = parts.get(key, "") + text
    return [text for text in parts.values() if text]


def _join(parts: list[str]) -> str:
    """Join the parts of a reply continued past the output cap. A part that stops mid-line is
    sometimes continued by restarting that line; keep one copy of it."""
    text = ""
    for part in parts:
        partial = text[text.rfind("\n") + 1 :]
        if partial and part.startswith(partial):
            text = text[: len(text) - len(partial)]
        text += part
    return text


def _resumable(messages: list[Message]) -> _Session | None:
    with _lock:
        session = _sessions.get(id(messages))
    if (
        session
        and len(messages) > len(session.prefix)
        and messages[: len(session.prefix)] == session.prefix
    ):
        return session
    return None


def _remember(messages: list[Message], reply: Message, session_id: str, cost_usd: float) -> None:
    if not session_id:
        return
    with _lock:
        if len(_sessions) >= MAX_SESSIONS and id(messages) not in _sessions:
            _sessions.pop(next(iter(_sessions)))
        _sessions[id(messages)] = _Session(session_id, copy.deepcopy([*messages, reply]), cost_usd)
