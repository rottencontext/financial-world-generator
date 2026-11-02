import asyncio
import json
from typing import Any

import httpx2 as httpx
import pytest

from worldgen.llm.base import LlmConfigError, LlmError
from worldgen.llm.chat_completions import ChatCompletionsLlm
from worldgen.llm.settings import settings_for

TOOLS = [{"name": "tell_story", "description": "Tell it", "input_schema": {"type": "object"}}]
ENV = {"OPENROUTER_API_KEY": "test-key"}


@pytest.fixture(autouse=True)
def no_retry_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    async def sleep(seconds: float) -> None:
        pass

    monkeypatch.setattr(asyncio, "sleep", sleep)


def response(message: dict[str, Any], finish: str = "stop") -> dict[str, Any]:
    return {
        "id": "completion-1",
        "model": "served-model",
        "choices": [{"message": {"role": "assistant", **message}, "finish_reason": finish}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


def test_endpoint_auth_model_and_tool_schema() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://openrouter.ai/api/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer test-key"
        payload = json.loads(request.content)
        assert payload["model"] == "custom-model"
        assert payload["messages"] == [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "hello"},
        ]
        assert payload["tools"] == [
            {
                "type": "function",
                "function": {
                    "name": "tell_story",
                    "description": "Tell it",
                    "parameters": {"type": "object"},
                },
            }
        ]
        for unsupported in ("thinking", "output_config", "betas", "fallbacks", "cache_control"):
            assert unsupported not in payload
        return httpx.Response(
            200, json=response({"content": "Done."}), headers={"x-request-id": "r1"}
        )

    llm = ChatCompletionsLlm(
        settings_for("openrouter", "custom-model"), env=ENV, transport=httpx.MockTransport(handle)
    )
    reply = asyncio.run(llm.complete("system", TOOLS, [{"role": "user", "content": "hello"}]))
    assert reply.content == [{"type": "text", "text": "Done."}]
    assert reply.stop_reason == "end_turn"
    assert reply.model == "served-model" and reply.request_id == "r1"
    assert reply.usage["input_tokens"] == 10 and reply.usage["output_tokens"] == 5


def test_parallel_tools_and_provider_metadata_survive_followup() -> None:
    assistant = {
        "role": "assistant",
        "content": None,
        "reasoning_details": [{"type": "reasoning.encrypted", "data": "opaque"}],
        "tool_calls": [
            {
                "id": "t1",
                "type": "function",
                "function": {"name": "tell_story", "arguments": '{ "story": "A world." }'},
            },
            {
                "id": "t2",
                "type": "function",
                "function": {"name": "spawn_child", "arguments": '{"items": []}'},
            },
        ],
    }
    calls = []

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(json.loads(request.content))
        return httpx.Response(200, json=response(assistant, "tool_calls"))

    llm = ChatCompletionsLlm(
        settings_for("openrouter"), env=ENV, transport=httpx.MockTransport(handle)
    )

    async def run() -> None:
        reply = await llm.complete("system", TOOLS, [{"role": "user", "content": "hello"}])
        assert reply.stop_reason == "tool_use"
        assert reply.tool_uses()[0] == {
            "type": "tool_use",
            "id": "t1",
            "name": "tell_story",
            "input": {"story": "A world."},
        }
        await llm.complete(
            "system",
            TOOLS,
            [
                {
                    "role": "assistant",
                    "content": reply.content,
                    "provider_message": reply.provider_message,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "tool_result", "tool_use_id": "t1", "content": "saved"},
                        {
                            "type": "tool_result",
                            "tool_use_id": "t2",
                            "content": "Rejected: bad",
                            "is_error": True,
                        },
                        {"type": "text", "text": "Continue."},
                    ],
                },
            ],
        )

    asyncio.run(run())
    assert calls[1]["messages"][1:] == [
        assistant,
        {"role": "tool", "tool_call_id": "t1", "content": "saved"},
        {"role": "tool", "tool_call_id": "t2", "content": "Rejected: bad"},
        {"role": "user", "content": "Continue."},
    ]


@pytest.mark.parametrize(
    ("finish", "expected"), [("length", "max_tokens"), ("content_filter", "refusal")]
)
def test_cutoff_or_filtered_tools_are_not_executed(finish: str, expected: str) -> None:
    payload = response(
        {"content": None, "tool_calls": [{"function": {"arguments": '{"cut'}}]}, finish
    )
    llm = ChatCompletionsLlm(
        settings_for("openrouter"),
        env=ENV,
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload)),
    )
    reply = asyncio.run(llm.complete("system", TOOLS, []))
    assert reply.stop_reason == expected and reply.tool_uses() == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"choices": []},
        {"error": {"message": "bad"}},
        response(
            {
                "content": None,
                "tool_calls": [
                    {"id": "t1", "function": {"name": "tell_story", "arguments": "not json"}}
                ],
            },
            "tool_calls",
        ),
    ],
)
def test_malformed_responses_become_llm_errors(payload: dict[str, Any]) -> None:
    llm = ChatCompletionsLlm(
        settings_for("openrouter"),
        env=ENV,
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload)),
    )
    with pytest.raises(LlmError):
        asyncio.run(llm.complete("system", TOOLS, []))


@pytest.mark.parametrize("status", [401, 429, 500])
def test_http_errors_do_not_echo_response_bodies_or_credentials(status: int) -> None:
    llm = ChatCompletionsLlm(
        settings_for("openrouter"),
        env=ENV,
        transport=httpx.MockTransport(lambda request: httpx.Response(status, text="test-key")),
    )
    with pytest.raises(LlmError, match=str(status)) as error:
        asyncio.run(llm.complete("system", TOOLS, []))
    assert "test-key" not in str(error.value)


def test_network_errors_become_llm_errors() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=request)

    llm = ChatCompletionsLlm(
        settings_for("openrouter"), env=ENV, transport=httpx.MockTransport(handle)
    )
    with pytest.raises(LlmError, match="ConnectError"):
        asyncio.run(llm.complete("system", TOOLS, []))


def test_missing_key_is_a_config_error() -> None:
    with pytest.raises(LlmConfigError, match="OPENROUTER_API_KEY"):
        ChatCompletionsLlm(settings_for("openrouter"), env={})


@pytest.mark.parametrize("field", ["id", "name"])
def test_malformed_tool_identifiers_fail_before_reaching_the_engine(field: str) -> None:
    call: dict[str, Any] = {
        "id": "t1",
        "function": {"name": "tell_story", "arguments": '{"story": "x"}'},
    }
    if field == "id":
        call["id"] = ["invalid"]
    else:
        call["function"]["name"] = ["invalid"]
    llm = ChatCompletionsLlm(
        settings_for("openrouter"),
        env=ENV,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=response({"tool_calls": [call]}, "tool_calls"))
        ),
    )
    with pytest.raises(LlmError):
        asyncio.run(llm.complete("system", TOOLS, []))


@pytest.mark.parametrize(
    ("effort", "expected"), [("low", "low"), ("high", "high"), ("xhigh", "high"), ("max", "high")]
)
def test_reasoning_effort_and_output_budget(effort: str, expected: str) -> None:
    llm = ChatCompletionsLlm(settings_for("openrouter", effort=effort), env=ENV)
    params = llm.request_params("system", [], [])
    assert params["reasoning"] == {"effort": expected}
    assert params["max_tokens"] == 64000
    assert "tools" not in params


@pytest.mark.parametrize("status", [429, 503])
def test_transient_status_is_retried_with_the_same_request(status: int) -> None:
    bodies = []

    def handle(request: httpx.Request) -> httpx.Response:
        bodies.append(request.content)
        if len(bodies) < 3:
            return httpx.Response(
                status,
                headers={"retry-after": "invalid"},
                json={"error": {"message": "temporarily unavailable"}},
            )
        return httpx.Response(200, json=response({"content": "Done.", "reasoning": "thought"}))

    llm = ChatCompletionsLlm(
        settings_for("openrouter"), env=ENV, transport=httpx.MockTransport(handle)
    )
    reply = asyncio.run(llm.complete("system", TOOLS, []))
    assert reply.stop_reason == "end_turn"
    assert reply.content[0] == {"type": "thinking", "thinking": "thought"}
    assert len(bodies) == 3 and bodies[0] == bodies[1] == bodies[2]


def test_retries_stop_after_three_attempts() -> None:
    calls = 0

    def handle(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503, json={"error": {"message": "Model overloaded"}})

    llm = ChatCompletionsLlm(
        settings_for("openrouter"), env=ENV, transport=httpx.MockTransport(handle)
    )
    with pytest.raises(LlmError, match="Model overloaded"):
        asyncio.run(llm.complete("system", TOOLS, []))
    assert calls == 3


@pytest.mark.parametrize("status", [400, 402, 413])
def test_permanent_errors_explain_the_cause_without_retrying_or_exposing_secrets(
    status: int,
) -> None:
    calls = 0

    def handle(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            status,
            json={
                "error": {
                    "message": (
                        "Requested 64000 tokens; can afford 10666. Key test-key. "
                        "Details https://openrouter.ai/workspaces/default/keys/private-key-id"
                    )
                }
            },
        )

    llm = ChatCompletionsLlm(
        settings_for("openrouter"), env=ENV, transport=httpx.MockTransport(handle)
    )
    with pytest.raises(LlmError, match="can afford 10666") as error:
        asyncio.run(llm.complete("system", TOOLS, []))
    assert calls == 1
    assert "test-key" not in str(error.value) and "private-key-id" not in str(error.value)


def test_messages_converts_plain_assistant_tool_use_without_provider_message() -> None:
    llm = ChatCompletionsLlm(settings_for("openrouter"), env=ENV)
    params = llm.request_params(
        "system",
        TOOLS,
        [
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Here"},
                    {"type": "tool_use", "id": "t1", "name": "tell_story", "input": {"story": "s"}},
                ],
            }
        ],
    )
    assert params["messages"][1] == {
        "role": "assistant",
        "content": "Here",
        "tool_calls": [
            {
                "id": "t1",
                "type": "function",
                "function": {"name": "tell_story", "arguments": '{"story": "s"}'},
            }
        ],
    }


def test_refusal_field_marks_stop_reason_refusal() -> None:
    payload = response({"content": None, "refusal": "cannot comply"}, "stop")
    llm = ChatCompletionsLlm(
        settings_for("openrouter"),
        env=ENV,
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload)),
    )
    reply = asyncio.run(llm.complete("system", TOOLS, []))
    assert reply.stop_reason == "refusal"
    assert reply.stop_details == {"reason": "cannot comply"}
