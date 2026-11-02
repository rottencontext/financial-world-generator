import pytest

from worldgen.llm.base import LlmConfigError
from worldgen.llm.settings import (
    API_KEYS,
    DEFAULT_EFFORT,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODELS,
    Provider,
    pick_provider,
    settings_for,
)


@pytest.mark.parametrize("provider", ["anthropic", "deepseek", "openrouter"])
def test_each_provider_can_be_selected_or_detected(provider: Provider) -> None:
    env = {API_KEYS[provider][0]: "test-key"}
    assert pick_provider(env) == provider
    default = settings_for(env=env)
    assert default.model == DEFAULT_MODELS[provider]
    assert default.effort == DEFAULT_EFFORT == "low"
    assert default.max_tokens == DEFAULT_MAX_TOKENS == 64000
    settings = settings_for(provider, "custom-model", "high", env={})
    assert (settings.provider, settings.model, settings.effort) == (
        provider,
        "custom-model",
        "high",
    )


def test_cheapest_default_models() -> None:
    assert DEFAULT_MODELS == {
        "anthropic": "claude-haiku-5-5",
        "deepseek": "deepseek-flash",
        "openrouter": "deepseek/deepseek-v4.1-flash",
    }


def test_detection_preserves_existing_priority() -> None:
    env = {names[0]: "test-key" for names in API_KEYS.values()}
    assert pick_provider(env) == "anthropic"
    del env["ANTHROPIC_API_KEY"]
    assert pick_provider(env) == "deepseek"
    del env["DEEPSEEK_API_KEY"]
    assert pick_provider(env) == "openrouter"


def test_missing_credentials_names_available_providers() -> None:
    with pytest.raises(LlmConfigError, match="OPENROUTER_API_KEY"):
        pick_provider({})


def test_explicit_output_budget_overrides_the_default() -> None:
    assert settings_for("openrouter", max_tokens=4096).max_tokens == 4096
    with pytest.raises(LlmConfigError, match="positive"):
        settings_for("openrouter", max_tokens=0)
