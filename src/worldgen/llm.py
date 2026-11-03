"""One OpenRouter chat call: messages and tools in, the assistant message out.

API: https://openrouter.ai/docs/api/reference/overview
"""

import os
import time
from typing import Any

import httpx2 as httpx

URL = "https://openrouter.ai/api/v1/chat/completions"

Message = dict[str, Any]


class LlmError(Exception):
    """The model call failed after retries, or no key is set."""


def chat(
    model: str,
    messages: list[Message],
    tools: list[dict[str, Any]] | None = None,
    effort: str = "low",
    tool_choice: str | None = None,
) -> tuple[Message, dict[str, Any]]:
    """Return the assistant message (kept verbatim for the next call) and the usage."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise LlmError("Set OPENROUTER_API_KEY, for example in .env, and run with --env-file .env")
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": 64000,
        "reasoning": {"effort": effort},
        "usage": {"include": True},
    }
    if tools:
        body["tools"] = tools
        if tool_choice:
            body["tool_choice"] = tool_choice
    for attempt in range(4):
        last = attempt == 3
        try:
            response = httpx.post(
                URL,
                headers={"Authorization": f"Bearer {key}"},
                json=body,
                timeout=httpx.Timeout(900, connect=30),
            )
        except httpx.RequestError as error:
            if last:
                raise LlmError(f"OpenRouter {type(error).__name__} after 4 attempts") from error
            time.sleep(2 ** (attempt + 1))
            continue
        if (response.status_code == 429 or response.status_code >= 500) and not last:
            time.sleep(2 ** (attempt + 1))
            continue
        if not response.is_success:
            raise LlmError(f"OpenRouter HTTP {response.status_code}: {response.text[:500]}")
        try:
            data = response.json()
        except ValueError as error:
            if last:
                raise LlmError(f"OpenRouter non-JSON response: {response.text[:500]}") from error
            time.sleep(2 ** (attempt + 1))
            continue
        # OpenRouter can answer 200 with an error from the upstream provider.
        if data.get("error") or not data.get("choices"):
            if last:
                raise LlmError(f"OpenRouter error: {str(data.get('error'))[:500]}")
            time.sleep(2 ** (attempt + 1))
            continue
        choice = data["choices"][0]
        usage = dict(data.get("usage") or {})
        usage["finish_reason"] = choice.get("finish_reason")
        return choice["message"], usage
    raise AssertionError("unreachable")
