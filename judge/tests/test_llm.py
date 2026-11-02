import asyncio
import json
from types import SimpleNamespace
from typing import Any

import anthropic
import httpx2 as httpx
import pytest

from llm_judge.llm import (
    API_KEYS,
    DEEPSEEK_BASE_URL,
    DEFAULT_MODELS,
    AnthropicLlm,
    ChatCompletionsLlm,
    LlmConfigError,
    LlmError,
    Settings,
    create_llm,
    make_client,
    pick_provider,
    settings_for,
)

SCHEMA = {"type": "object"}
ENV = {"OPENROUTER_API_KEY": "test-key"}


class Usage:
    def to_dict(self) -> dict[str, Any]:
        return {"input_tokens": 10, "output_tokens": 5}


class Stream:
    def __init__(self, message: Any, error: Exception | None):
        self.message, self.error = message, error

    async def __aenter__(self) -> "Stream":
        if self.error:
            raise self.error
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def get_final_message(self) -> Any:
        return self.message

    @property
    def request_id(self) -> str:
        return "req_1"


class Messages:
    def __init__(self, stop: str = "end_turn", error: Exception | None = None):
        self.calls: list[dict[str, Any]] = []
        self.stop, self.error = stop, error

    def stream(self, **params: Any) -> Stream:
        self.calls.append(params)
        message = SimpleNamespace(
            content=[
                SimpleNamespace(type="thinking", thinking="hmm"),
                SimpleNamespace(type="text", text='{"a": '),
                SimpleNamespace(type="text", text="1}"),
            ],
            stop_reason=self.stop,
            usage=Usage(),
            model="m",
        )
        return Stream(message, self.error)


class Client:
    def __init__(self, stop: str = "end_turn", error: Exception | None = None):
        self.messages = Messages(stop, error)
        self.beta = SimpleNamespace(messages=Messages(stop, error))


def test_pick_provider_and_cheapest_defaults() -> None:
    assert pick_provider({"ANTHROPIC_API_KEY": "a", "DEEPSEEK_API_KEY": "d"}) == "anthropic"
    assert pick_provider({"DEEPSEEK_API_KEY": "d"}) == "deepseek"
    for provider, names in API_KEYS.items():
        assert pick_provider({names[0]: "k"}) == provider
        s = settings_for(env={names[0]: "k"})
        assert s.model == DEFAULT_MODELS[provider]
        assert s.effort == "low"
    assert DEFAULT_MODELS == {
        "anthropic": "claude-haiku-5-5",
        "deepseek": "deepseek-flash",
        "openrouter": "deepseek/deepseek-v4.1-flash",
    }
    assert settings_for("openrouter").max_tokens == 64000
    assert settings_for("openrouter", max_tokens=4096).max_tokens == 4096
    with pytest.raises(LlmConfigError, match="positive"):
        settings_for("openrouter", max_tokens=0)
    with pytest.raises(LlmConfigError):
        pick_provider({})


def test_make_client_and_create_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    client = make_client("deepseek", {"DEEPSEEK_API_KEY": "d"})
    assert str(client.base_url).rstrip("/") == DEEPSEEK_BASE_URL
    with pytest.raises(LlmConfigError):
        make_client("deepseek", {})
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    assert isinstance(create_llm(settings_for("anthropic")), AnthropicLlm)
    monkeypatch.setenv("OPENROUTER_API_KEY", "o")
    assert isinstance(create_llm(settings_for("openrouter")), ChatCompletionsLlm)


def test_anthropic_request_uses_structured_output() -> None:
    client = Client()
    llm = AnthropicLlm(Settings("anthropic", "claude-haiku-5-5"), client)  # type: ignore[arg-type]
    reply = asyncio.run(llm.complete("sys", "user", SCHEMA))
    params = client.beta.messages.calls[0]
    assert params["output_config"] == {
        "effort": "low",
        "format": {"type": "json_schema", "schema": SCHEMA},
    }
    assert params["thinking"] == {"type": "adaptive"}
    assert params["fallbacks"] == "default"
    assert (reply.text, reply.request_id, reply.usage["input_tokens"]) == ('{"a": 1}', "req_1", 10)
    assert llm.name == "anthropic:claude-haiku-5-5"


def test_deepseek_request_has_only_shared_fields() -> None:
    client = Client()
    llm = AnthropicLlm(Settings("deepseek", "deepseek-flash", "low"), client)  # type: ignore[arg-type]
    asyncio.run(llm.complete("sys", "user", SCHEMA))
    params = client.messages.calls[0]
    assert params["output_config"] == {"effort": "low"}
    assert params["thinking"] == {"type": "enabled"}
    assert "fallbacks" not in params and "betas" not in params


@pytest.mark.parametrize(("stop", "message"), [("refusal", "declined"), ("max_tokens", "cut off")])
def test_unusable_stop_reasons(stop: str, message: str) -> None:
    llm = AnthropicLlm(Settings("deepseek", "m"), Client(stop=stop))  # type: ignore[arg-type]
    with pytest.raises(LlmError, match=message):
        asyncio.run(llm.complete("s", "u", SCHEMA))


def test_api_error_becomes_llm_error() -> None:
    request = httpx.Request("POST", "https://example.com")
    error = anthropic.APIConnectionError(request=request)
    llm = AnthropicLlm(Settings("anthropic", "m"), Client(error=error))  # type: ignore[arg-type]
    with pytest.raises(LlmError, match="APIConnectionError"):
        asyncio.run(llm.complete("s", "u", SCHEMA))


def status_error(code: int) -> anthropic.APIStatusError:
    request = httpx.Request("POST", "https://example.com")
    response = httpx.Response(code, request=request)
    return anthropic.APIStatusError("status", response=response, body=None)


@pytest.mark.parametrize(
    ("error", "transient"),
    [
        (anthropic.APIConnectionError(request=httpx.Request("POST", "https://x")), True),
        (httpx.ReadTimeout("stalled mid-stream"), True),
        (status_error(529), True),
        (status_error(429), True),
        (status_error(400), False),
    ],
)
def test_errors_are_marked_transient_or_not(error: Exception, transient: bool) -> None:
    llm = AnthropicLlm(Settings("deepseek", "m"), Client(error=error))  # type: ignore[arg-type]
    with pytest.raises(LlmError) as caught:
        asyncio.run(llm.complete("s", "u", SCHEMA))
    assert caught.value.transient is transient


def test_openrouter_request_and_reply() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://openrouter.ai/api/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer test-key"
        body = json.loads(request.content)
        assert body["messages"] == [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "usr"},
        ]
        assert body["reasoning"] == {"effort": "high"}
        assert body["max_tokens"] == 64000
        return httpx.Response(
            200,
            headers={"x-request-id": "r1"},
            json={
                "id": "c1",
                "model": "served",
                "choices": [{"message": {"content": '{"ok": true}'}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 6},
            },
        )

    llm = ChatCompletionsLlm(
        settings_for("openrouter", effort="xhigh"), env=ENV, transport=httpx.MockTransport(handle)
    )
    reply = asyncio.run(llm.complete("sys", "usr", SCHEMA))
    assert (reply.text, reply.request_id, reply.model) == ('{"ok": true}', "r1", "served")
    assert (reply.usage["input_tokens"], reply.usage["output_tokens"]) == (12, 6)


def test_chat_completions_config_and_error_paths() -> None:
    with pytest.raises(LlmConfigError, match="OPENROUTER_API_KEY"):
        ChatCompletionsLlm(settings_for("openrouter"), env={})

    def net_err(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    llm = ChatCompletionsLlm(
        settings_for("openrouter"), env=ENV, transport=httpx.MockTransport(net_err)
    )
    with pytest.raises(LlmError) as caught:
        asyncio.run(llm.complete("s", "u", SCHEMA))
    assert caught.value.transient is True

    for status, is_transient in [(429, True), (503, True), (402, False)]:
        llm_status = ChatCompletionsLlm(
            settings_for("openrouter"),
            env=ENV,
            transport=httpx.MockTransport(
                lambda req, st=status: httpx.Response(
                    st, json={"error": {"message": "limit test-key https://openrouter.ai/x"}}
                )
            ),
        )
        with pytest.raises(LlmError) as caught_status:
            asyncio.run(llm_status.complete("s", "u", SCHEMA))
        assert caught_status.value.transient is is_transient
        assert "test-key" not in str(caught_status.value)

    for finish, refusal, msg in [
        ("length", None, "cut off"),
        ("content_filter", None, "declined"),
        ("stop", "no", "declined"),
    ]:
        llm_stop = ChatCompletionsLlm(
            settings_for("openrouter"),
            env=ENV,
            transport=httpx.MockTransport(
                lambda req, f=finish, r=refusal: httpx.Response(
                    200,
                    json={
                        "id": "c1",
                        "choices": [{"message": {"content": "", "refusal": r}, "finish_reason": f}],
                    },
                )
            ),
        )
        with pytest.raises(LlmError, match=msg):
            asyncio.run(llm_stop.complete("s", "u", SCHEMA))

    for bad_payload in [
        {},
        {"choices": [{"message": {"content": 123}, "finish_reason": "stop"}]},
    ]:
        llm_bad = ChatCompletionsLlm(
            settings_for("openrouter"),
            env=ENV,
            transport=httpx.MockTransport(lambda req, p=bad_payload: httpx.Response(200, json=p)),
        )
        with pytest.raises(LlmError, match="invalid Chat Completions"):
            asyncio.run(llm_bad.complete("s", "u", SCHEMA))
