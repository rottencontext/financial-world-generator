"""AnthropicLlm: the Llm interface on the Anthropic Python SDK.

Two providers speak the Anthropic Messages API, and this one class serves both:

- anthropic: Claude. The default model is claude-haiku-5-5. Requests use adaptive thinking
  with summarized display (so log.jsonl shows why an agent acted), an explicit effort, prompt
  caching (the system prompt and tools are identical on every turn) and server-side refusal
  fallback.
- deepseek: DeepSeek's Anthropic-compatible endpoint (default deepseek-flash). It accepts thinking
  and output_config.effort, ignores cache_control and a tool_result's is_error, and does not
  document betas or fallbacks, so requests carry only the shared fields.
"""

import os
from collections.abc import Mapping
from typing import Any

import anthropic

from worldgen.llm.base import LlmConfigError, LlmError, LlmReply, Message
from worldgen.llm.settings import DEFAULT_MODELS, LlmSettings, Provider, pick_provider, settings_for

__all__ = [
    "DEEPSEEK_BASE_URL",
    "DEFAULT_MODELS",
    "AnthropicLlm",
    "LlmSettings",
    "Provider",
    "make_client",
    "pick_provider",
    "settings_for",
]

DEEPSEEK_BASE_URL = "https://api.deepseek.com/anthropic"

FALLBACK_BETA = "server-side-fallback-2026-07-01"


def make_client(
    provider: Provider, env: Mapping[str, str] | None = None
) -> anthropic.AsyncAnthropic:
    env = os.environ if env is None else env
    if provider == "deepseek":
        key = env.get("DEEPSEEK_API_KEY")
        if not key:
            raise LlmConfigError("Provider deepseek needs DEEPSEEK_API_KEY.")
        return anthropic.AsyncAnthropic(api_key=key, base_url=DEEPSEEK_BASE_URL)
    # Credentials come from ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN or an `ant auth login` profile.
    return anthropic.AsyncAnthropic()


class AnthropicLlm:
    def __init__(self, settings: LlmSettings, client: anthropic.AsyncAnthropic | None = None):
        self.settings = settings
        self.name = f"{settings.provider}:{settings.model}"
        self._client = client or make_client(settings.provider)

    def request_params(
        self, system: str, tools: list[dict[str, Any]], messages: list[Message]
    ) -> dict[str, Any]:
        s = self.settings
        params: dict[str, Any] = {
            "model": s.model,
            "max_tokens": s.max_tokens,
            "system": system,
            "tools": tools,
            "messages": messages,
            "output_config": {"effort": s.effort},
        }
        if s.provider == "anthropic":
            params["thinking"] = {"type": "adaptive", "display": "summarized"}
            params["cache_control"] = {"type": "ephemeral"}
            params["betas"] = [FALLBACK_BETA]
            params["fallbacks"] = "default"
            # Long tool inputs (a story, a child's prompt) stream as they are written. The API
            # then skips input validation, so every tool validates its own input.
            params["tools"] = [{**tool, "eager_input_streaming": True} for tool in tools]
        else:
            params["thinking"] = {"type": "enabled"}
        return params

    async def complete(
        self, system: str, tools: list[dict[str, Any]], messages: list[Message]
    ) -> LlmReply:
        params = self.request_params(system, tools, messages)
        try:
            if self.settings.provider == "anthropic":
                async with self._client.beta.messages.stream(**params) as stream:
                    message: Any = await stream.get_final_message()
                    request_id = stream.request_id
            else:
                async with self._client.messages.stream(**params) as stream:
                    message = await stream.get_final_message()
                    request_id = stream.request_id
        except anthropic.APIError as error:
            raise LlmError(f"{type(error).__name__}: {error}") from error
        stop_details = getattr(message, "stop_details", None)
        return LlmReply(
            content=[block.to_dict() for block in message.content],
            stop_reason=message.stop_reason or "",
            usage=message.usage.to_dict(),
            request_id=request_id,
            model=message.model,
            stop_details=stop_details.to_dict() if stop_details is not None else None,
        )
