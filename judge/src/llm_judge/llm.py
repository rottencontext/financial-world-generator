"""The judge's model call: one system prompt and one user message in, reply text out.

Three providers, two adapters:

- anthropic & deepseek (AnthropicLlm): Anthropic Messages API. Claude (default claude-haiku-5-5)
  uses adaptive thinking, an explicit effort, the verdict's JSON schema as a structured output,
  prompt caching, and server-side refusal fallback. DeepSeek (default deepseek-flash) uses its
  Anthropic-compatible endpoint with thinking and effort.
- openrouter (ChatCompletionsLlm): OpenRouter's Chat Completions API (default
  deepseek/deepseek-v4.1-flash) with reasoning effort; the verdict's shape comes from the prompt.
"""

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

import anthropic
import httpx2 as httpx

Provider = Literal["anthropic", "deepseek", "openrouter"]
Effort = Literal["low", "medium", "high", "xhigh", "max"]

DEEPSEEK_BASE_URL = "https://api.deepseek.com/anthropic"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

API_KEYS: dict[Provider, tuple[str, ...]] = {
    "anthropic": ("ANTHROPIC_API_KEY",),
    "deepseek": ("DEEPSEEK_API_KEY",),
    "openrouter": ("OPENROUTER_API_KEY",),
}

DEFAULT_MODELS: dict[Provider, str] = {
    "anthropic": "claude-haiku-5-5",
    "deepseek": "deepseek-flash",
    "openrouter": "deepseek/deepseek-v4.1-flash",
}

DEFAULT_EFFORT: Effort = "low"

DEFAULT_MAX_TOKENS = 64000

FALLBACK_BETA = "server-side-fallback-2026-07-01"


class LlmError(Exception):
    """The model call failed or its reply can't be used (refusal, cut off, API error).

    `transient` marks failures worth trying again: network errors, a stream that stalls or
    drops, rate limits and server errors.
    """

    def __init__(self, message: str, transient: bool = False):
        super().__init__(message)
        self.transient = transient


class LlmConfigError(Exception):
    """No usable model configuration, such as a missing API key."""


@dataclass(frozen=True)
class Settings:
    provider: Provider
    model: str
    effort: Effort = DEFAULT_EFFORT
    max_tokens: int = DEFAULT_MAX_TOKENS


@dataclass(frozen=True)
class Reply:
    text: str
    stop_reason: str
    usage: dict[str, Any] = field(default_factory=dict)
    request_id: str | None = None
    model: str | None = None


class Llm(Protocol):
    name: str
    """provider:model, recorded with every verdict."""

    async def complete(self, system: str, user: str, schema: dict[str, Any]) -> Reply: ...


def pick_provider(env: Mapping[str, str] | None = None) -> Provider:
    env = os.environ if env is None else env
    for provider, names in API_KEYS.items():
        if any(env.get(name) for name in names):
            return provider
    key_names = ", ".join(names[0] for names in API_KEYS.values())
    raise LlmConfigError(
        f"No model credentials. Set one of {key_names}, for example in .env "
        "and run with `uv run --env-file ../.env judge ...`."
    )


def settings_for(
    provider: Provider | None = None,
    model: str | None = None,
    effort: Effort = DEFAULT_EFFORT,
    env: Mapping[str, str] | None = None,
    *,
    max_tokens: int | None = None,
) -> Settings:
    chosen = provider or pick_provider(env)
    if max_tokens is None:
        max_tokens = DEFAULT_MAX_TOKENS
    if max_tokens < 1:
        raise LlmConfigError("max_tokens must be positive.")
    return Settings(
        provider=chosen,
        model=model or DEFAULT_MODELS[chosen],
        effort=effort,
        max_tokens=max_tokens,
    )


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
    def __init__(self, settings: Settings, client: anthropic.AsyncAnthropic | None = None):
        self.settings = settings
        self.name = f"{settings.provider}:{settings.model}"
        self._client = client or make_client(settings.provider)

    def request_params(self, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]:
        s = self.settings
        params: dict[str, Any] = {
            "model": s.model,
            "max_tokens": s.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "output_config": {"effort": s.effort},
        }
        if s.provider == "anthropic":
            params["thinking"] = {"type": "adaptive"}
            params["output_config"]["format"] = {"type": "json_schema", "schema": schema}
            params["cache_control"] = {"type": "ephemeral"}
            params["betas"] = [FALLBACK_BETA]
            params["fallbacks"] = "default"
        else:
            params["thinking"] = {"type": "enabled"}
        return params

    async def complete(self, system: str, user: str, schema: dict[str, Any]) -> Reply:
        params = self.request_params(system, user, schema)
        try:
            if self.settings.provider == "anthropic":
                async with self._client.beta.messages.stream(**params) as stream:
                    message: Any = await stream.get_final_message()
                    request_id = stream.request_id
            else:
                async with self._client.messages.stream(**params) as stream:
                    message = await stream.get_final_message()
                    request_id = stream.request_id
        except anthropic.APIConnectionError as error:  # includes APITimeoutError
            raise LlmError(f"{type(error).__name__}: {error}", transient=True) from error
        except anthropic.APIStatusError as error:
            transient = error.status_code == 429 or error.status_code >= 500
            raise LlmError(f"{type(error).__name__}: {error}", transient) from error
        except anthropic.APIError as error:
            raise LlmError(f"{type(error).__name__}: {error}") from error
        except httpx.HTTPError as error:
            # A stream that stalls or drops after the response has started surfaces as an
            # httpx2 error, not an SDK one, and the SDK does not retry it.
            raise LlmError(f"{type(error).__name__}: {error}", transient=True) from error
        stop = message.stop_reason or ""
        if stop == "refusal":
            raise LlmError(f"the model declined to judge (request {request_id})")
        if stop == "max_tokens":
            raise LlmError(f"the reply was cut off at max_tokens (request {request_id})")
        text = "".join(block.text for block in message.content if block.type == "text")
        return Reply(
            text=text,
            stop_reason=stop,
            usage=message.usage.to_dict(),
            request_id=request_id,
            model=message.model,
        )


class ChatCompletionsLlm:
    def __init__(
        self,
        settings: Settings,
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

    def request_params(self, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]:
        s = self.settings
        params: dict[str, Any] = {
            "model": s.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": s.max_tokens,
        }
        # OpenRouter takes low/medium/high and maps it to each model's reasoning controls.
        effort = "high" if s.effort in ("xhigh", "max") else s.effort
        params["reasoning"] = {"effort": effort}
        return params

    async def complete(self, system: str, user: str, schema: dict[str, Any]) -> Reply:
        params = self.request_params(system, user, schema)
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(600, connect=30), transport=self._transport
            ) as client:
                response = await client.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {self._key}"},
                    json=params,
                )
        except httpx.HTTPError as error:
            raise LlmError(
                f"{self.settings.provider} {type(error).__name__}", transient=True
            ) from error
        if not response.is_success:
            transient = response.status_code == 429 or response.status_code >= 500
            detail = _error_detail(response, self._key)
            raise LlmError(
                f"{self.settings.provider} HTTP {response.status_code}"
                + (f": {detail}" if detail else ""),
                transient=transient,
            )
        try:
            data = response.json()
            choice = data["choices"][0]
            message = choice["message"]
            finish = choice["finish_reason"]
            stop = {
                "stop": "end_turn",
                "length": "max_tokens",
                "content_filter": "refusal",
            }[finish]
            if message.get("refusal"):
                stop = "refusal"
            content = message.get("content") or ""
            if not isinstance(content, str):
                raise ValueError("Expected text content")
        except (KeyError, IndexError, TypeError, ValueError, AttributeError) as error:
            raise LlmError(
                f"{self.settings.provider} returned an invalid Chat Completions response."
            ) from error
        request_id = response.headers.get("x-request-id") or data.get("id")
        if stop == "refusal":
            raise LlmError(f"the model declined to judge (request {request_id})")
        if stop == "max_tokens":
            raise LlmError(f"the reply was cut off at max_tokens (request {request_id})")
        usage = data.get("usage") or {}
        return Reply(
            text=content,
            stop_reason=stop,
            usage={
                **usage,
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
            },
            request_id=request_id,
            model=data.get("model"),
        )


def _error_detail(response: httpx.Response, key: str) -> str:
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


def create_llm(settings: Settings) -> Llm:
    if settings.provider in ("anthropic", "deepseek"):
        return AnthropicLlm(settings)
    return ChatCompletionsLlm(settings)
