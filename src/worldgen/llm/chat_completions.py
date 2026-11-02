"""Translate the narrator's messages to OpenRouter's Chat Completions API.

Endpoint and tool-call contract: https://openrouter.ai/docs/api/reference/overview
"""

import asyncio
import json
import os
import re
from collections.abc import Mapping
from typing import Any

import httpx2 as httpx

from worldgen.llm.base import Block, LlmConfigError, LlmError, LlmReply, Message
from worldgen.llm.settings import API_KEYS, LlmSettings

BASE_URL = "https://openrouter.ai/api/v1"


class ChatCompletionsLlm:
    def __init__(
        self,
        settings: LlmSettings,
        *,
        env: Mapping[str, str] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self.settings = settings
        self.name = f"{settings.provider}:{settings.model}"
        env = os.environ if env is None else env
        names = API_KEYS[settings.provider]
        key = next((env[name] for name in names if env.get(name)), None)
        if not key:
            raise LlmConfigError(f"Provider {settings.provider} needs {' or '.join(names)}.")
        self._key = key
        self._transport = transport

    def request_params(
        self, system: str, tools: list[dict[str, Any]], messages: list[Message]
    ) -> dict[str, Any]:
        s = self.settings
        params: dict[str, Any] = {
            "model": s.model,
            "messages": [{"role": "system", "content": system}, *_messages(messages)],
            "max_tokens": s.max_tokens,
        }
        if tools:
            params["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["input_schema"],
                    },
                }
                for tool in tools
            ]
        # OpenRouter takes low/medium/high and maps it to each model's reasoning controls.
        # https://openrouter.ai/docs/guides/best-practices/reasoning-tokens
        effort = "high" if s.effort in ("xhigh", "max") else s.effort
        params["reasoning"] = {"effort": effort}
        return params

    async def complete(
        self, system: str, tools: list[dict[str, Any]], messages: list[Message]
    ) -> LlmReply:
        params = self.request_params(system, tools, messages)
        # Bounded retries for transient provider failures; billing/input errors need user action.
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(600, connect=30), transport=self._transport
        ) as client:
            for attempt in range(3):
                try:
                    response = await client.post(
                        f"{BASE_URL}/chat/completions",
                        headers={"Authorization": f"Bearer {self._key}"},
                        json=params,
                    )
                except httpx.RequestError as error:
                    if attempt == 2:
                        raise LlmError(
                            f"{self.settings.provider} {type(error).__name__} after 3 attempts"
                        ) from error
                    await asyncio.sleep(2**attempt)
                    continue
                if (response.status_code == 429 or response.status_code >= 500) and attempt < 2:
                    try:
                        delay = float(response.headers.get("retry-after", 2**attempt))
                    except ValueError:
                        delay = 2**attempt
                    await asyncio.sleep(max(0, min(delay, 30)))
                    continue
                if not response.is_success:
                    detail = _error_detail(response, self._key)
                    raise LlmError(
                        f"{self.settings.provider} HTTP {response.status_code}"
                        + (f": {detail}" if detail else "")
                    )
                break
        try:
            return _reply(response.json(), response.headers.get("x-request-id"))
        except (KeyError, IndexError, TypeError, ValueError, AttributeError) as error:
            raise LlmError(
                f"{self.settings.provider} returned an invalid Chat Completions response."
            ) from error


def _error_detail(response: httpx.Response, key: str) -> str:
    """Retain actionable provider messages, excluding headers, credentials, and account URLs."""
    try:
        body = response.json()
    except ValueError:
        return ""
    if not isinstance(body, dict):
        return ""
    error = body.get("error")
    if not isinstance(error, dict) or not isinstance(error.get("message"), str):
        return ""
    text = error["message"].replace(key, "[REDACTED]")
    text = re.sub(r"https?://[^\s\"<>]+", "[URL]", text)
    text = re.sub(r"sk-[A-Za-z0-9_-]{12,}", "[REDACTED]", text)
    return " ".join(text.split())[:1500]


def _messages(messages: list[Message]) -> list[Message]:
    converted: list[Message] = []
    for message in messages:
        if message.get("provider_message") is not None:
            # Preserve OpenRouter's reasoning_details verbatim.
            converted.append(message["provider_message"])
            continue
        content = message["content"]
        if isinstance(content, str):
            converted.append({"role": message["role"], "content": content})
            continue
        text = "\n".join(block["text"] for block in content if block["type"] == "text")
        if message["role"] == "assistant":
            assistant: Message = {"role": "assistant", "content": text or None}
            calls = [
                {
                    "id": block["id"],
                    "type": "function",
                    "function": {"name": block["name"], "arguments": json.dumps(block["input"])},
                }
                for block in content
                if block["type"] == "tool_use"
            ]
            if calls:
                assistant["tool_calls"] = calls
            converted.append(assistant)
        else:
            converted.extend(
                {"role": "tool", "tool_call_id": block["tool_use_id"], "content": block["content"]}
                for block in content
                if block["type"] == "tool_result"
            )
            if text:
                converted.append({"role": "user", "content": text})
    return converted


def _reply(data: dict[str, Any], request_id: str | None) -> LlmReply:
    choice = data["choices"][0]
    message = choice["message"]
    finish = choice["finish_reason"]
    stop = {
        "stop": "end_turn",
        "tool_calls": "tool_use",
        "length": "max_tokens",
        "content_filter": "refusal",
    }[finish]
    if message.get("refusal"):
        stop = "refusal"
    blocks: list[Block] = []
    if message.get("reasoning"):
        blocks.append({"type": "thinking", "thinking": message["reasoning"]})
    if message.get("content"):
        if not isinstance(message["content"], str):
            raise ValueError("Expected text content")
        blocks.append({"type": "text", "text": message["content"]})
    # A cutoff may contain partial JSON. Preserve the cutoff without attempting to run any tools.
    if stop not in ("max_tokens", "refusal"):
        for call in message.get("tool_calls") or []:
            function = call["function"]
            arguments = json.loads(function["arguments"])
            if not isinstance(arguments, dict) or not all(
                isinstance(value, str) and value for value in (call["id"], function["name"])
            ):
                raise ValueError("Invalid function call")
            blocks.append(
                {"type": "tool_use", "id": call["id"], "name": function["name"], "input": arguments}
            )
        if finish == "tool_calls" and not any(b["type"] == "tool_use" for b in blocks):
            raise ValueError("Missing function calls")
    usage = data.get("usage") or {}
    return LlmReply(
        content=blocks,
        stop_reason=stop,
        usage={
            **usage,
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
            "cache_read_input_tokens": (usage.get("prompt_tokens_details") or {}).get(
                "cached_tokens", 0
            ),
        },
        request_id=request_id or data.get("id"),
        model=data.get("model"),
        stop_details={"reason": message.get("refusal") or finish} if stop == "refusal" else None,
        provider_message=message,
    )
