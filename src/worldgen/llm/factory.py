"""Build the adapter selected for a narrator run."""

from worldgen.llm.anthropic_llm import AnthropicLlm
from worldgen.llm.base import Llm
from worldgen.llm.chat_completions import ChatCompletionsLlm
from worldgen.llm.settings import LlmSettings


def create_llm(settings: LlmSettings) -> Llm:
    if settings.provider in ("anthropic", "deepseek"):
        return AnthropicLlm(settings)
    return ChatCompletionsLlm(settings)
