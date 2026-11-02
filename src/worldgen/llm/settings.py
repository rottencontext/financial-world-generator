"""Provider selection and model defaults; credentials are read only when needed."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from worldgen.llm.base import LlmConfigError

Provider = Literal["anthropic", "deepseek", "openrouter"]
Effort = Literal["low", "medium", "high", "xhigh", "max"]

# Insertion order is the auto-detection priority; keep the original two providers first.
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


@dataclass(frozen=True)
class LlmSettings:
    provider: Provider
    model: str
    effort: str = DEFAULT_EFFORT
    max_tokens: int = DEFAULT_MAX_TOKENS


def pick_provider(env: Mapping[str, str] | None = None) -> Provider:
    env = os.environ if env is None else env
    for provider, names in API_KEYS.items():
        if any(env.get(name) for name in names):
            return provider
    key_names = ", ".join(names[0] for names in API_KEYS.values())
    raise LlmConfigError(
        f"No model credentials. Set one of {key_names}, for example in .env "
        "and run with `uv run --env-file .env ...`."
    )


def settings_for(
    provider: Provider | None = None,
    model: str | None = None,
    effort: str = DEFAULT_EFFORT,
    env: Mapping[str, str] | None = None,
    *,
    max_tokens: int | None = None,
) -> LlmSettings:
    chosen = provider or pick_provider(env)
    if max_tokens is None:
        max_tokens = DEFAULT_MAX_TOKENS
    if max_tokens < 1:
        raise LlmConfigError("max_tokens must be positive.")
    return LlmSettings(chosen, model or DEFAULT_MODELS[chosen], effort, max_tokens)
