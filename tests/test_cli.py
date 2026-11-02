import json
from pathlib import Path
from typing import Any

import httpx2 as httpx
import pytest
from typer.testing import CliRunner

from worldgen import cli
from worldgen.llm.base import LlmReply
from worldgen.llm.chat_completions import ChatCompletionsLlm
from worldgen.llm.fake import FakeLlm, text_reply, tool_reply
from worldgen.llm.settings import API_KEYS, LlmSettings
from worldgen.tree.nodes import Tree

runner = CliRunner()


def scripted(*replies: Any) -> FakeLlm:
    llm = FakeLlm(list(replies))
    llm.name = "fake:test"
    return llm


@pytest.fixture
def fake_llm(monkeypatch: pytest.MonkeyPatch) -> list[FakeLlm]:
    llms: list[FakeLlm] = []

    def make(settings: Any) -> FakeLlm:
        return llms.pop(0)

    monkeypatch.setattr(cli, "create_llm", make)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
    return llms


ROOT_TURN = [
    tool_reply(
        ("tell_story", {"story": "A detailed story."}),
        (
            "spawn_child",
            {"items": [{"id": "n_sales", "role": "narrator", "name": "Sales", "prompt": "Sales."}]},
        ),
        ("brief_child", {"child": "n_sales", "brief": "Q1 renewals."}),
    ),
    text_reply(),
]
SALES_TURN = [tool_reply(("tell_story", {"story": "Sales story."})), text_reply()]
# The root spawns and briefs n_sales, then its next call is refused: the root fails and
# n_sales is left pending.
ROOT_FAILS = [ROOT_TURN[0], LlmReply(content=[], stop_reason="refusal")]


def test_narrate_goes_until_no_narrator_is_pending(tmp_path: Path, fake_llm: list[FakeLlm]) -> None:
    out = tmp_path / "story"
    fake_llm.append(scripted(*ROOT_TURN, *SALES_TURN))
    result = runner.invoke(cli.app, ["narrate", "--prompt", "A SaaS startup.", "--out", str(out)])
    assert result.exit_code == 0, result.output
    assert "Narrating n_root." in result.output and "never ran" not in result.output
    assert "n_root  Root narrator  [told] (story 3 words, 1 children)" in result.output
    assert Tree.load(out / "tree.json").node("n_sales").status == "told"
    assert (out / "story.md").read_text().startswith("# Root narrator: story tree")
    lines = (out / "log.jsonl").read_text().splitlines()
    kinds = [json.loads(line)["kind"] for line in lines]
    assert kinds[0] == "run_started" and kinds[-1] == "run_finished"
    assert json.loads(lines[0])["effort"] == "low"


def test_narrate_reports_narrators_left_pending_by_a_failed_parent(
    tmp_path: Path, fake_llm: list[FakeLlm]
) -> None:
    out = tmp_path / "story"
    fake_llm.append(scripted(*ROOT_FAILS))
    result = runner.invoke(cli.app, ["narrate", "--prompt", "A SaaS startup.", "--out", str(out)])
    assert result.exit_code == 0, result.output
    assert "! n_root failed: the model refused" in result.output
    assert "Narrators that never ran, because a narrator above failed: n_sales." in result.output
    assert Tree.load(out / "tree.json").node("n_sales").status == "pending"


def test_narrate_reads_prompt_and_brief_files_and_policies(
    tmp_path: Path, fake_llm: list[FakeLlm]
) -> None:
    prompt, brief = tmp_path / "p.md", tmp_path / "b.md"
    prompt.write_text("The sales department.")
    brief.write_text("Lumen Metrics sells analytics.")
    fake_llm.append(scripted(text_reply()))
    out = tmp_path / "s"
    args = [
        "narrate",
        "--prompt-file",
        str(prompt),
        "--brief-file",
        str(brief),
        "--out",
        str(out),
        "--policy",
        "unfinished_turn=accept",
        "--name",
        "Sales",
    ]
    result = runner.invoke(cli.app, args)
    assert result.exit_code == 0, result.output
    root = Tree.load(out / "tree.json").node("n_root")
    assert root.prompt == "The sales department." and root.brief == "Lumen Metrics sells analytics."
    assert root.status == "unfinished"
    assert "n_root unfinished: you have not told your story" in result.output


def test_narrate_rejects_bad_input(tmp_path: Path, fake_llm: list[FakeLlm]) -> None:
    out = str(tmp_path / "s")
    assert runner.invoke(cli.app, ["narrate", "--out", out]).exit_code != 0
    assert (
        runner.invoke(
            cli.app, ["narrate", "--out", out, "--prompt", "x", "--policy", "list_calls"]
        ).exit_code
        != 0
    )
    assert (
        runner.invoke(
            cli.app, ["narrate", "--out", out, "--prompt", "x", "--policy", "list_calls=some"]
        ).exit_code
        != 0
    )


def test_narrate_refuses_to_overwrite_a_tree(tmp_path: Path, fake_llm: list[FakeLlm]) -> None:
    out = tmp_path / "s"
    fake_llm.append(scripted(*ROOT_TURN, *SALES_TURN))
    runner.invoke(cli.app, ["narrate", "--prompt", "x", "--out", str(out)])
    again = runner.invoke(cli.app, ["narrate", "--prompt", "x", "--out", str(out)])
    assert again.exit_code != 0 and "already holds a tree" in again.output


def test_missing_credentials_exit_with_a_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for names in API_KEYS.values():
        for name in names:
            monkeypatch.delenv(name, raising=False)
    result = runner.invoke(cli.app, ["narrate", "--prompt", "x", "--out", str(tmp_path / "s")])
    assert result.exit_code == 1 and "No model credentials" in result.output


def test_openrouter_narrates_through_real_adapter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from worldgen.llm import factory

    provider = "openrouter"
    requests: list[dict[str, Any]] = []
    tool_message = {
        "role": "assistant",
        "content": None,
        "reasoning_details": [{"type": "reasoning.encrypted", "data": "opaque"}],
        "tool_calls": [
            {
                "id": "story-1",
                "type": "function",
                "function": {"name": "tell_story", "arguments": '{ "story": "A complete world." }'},
            }
        ],
    }

    def handle(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        requests.append(body)
        assert body["max_tokens"] == 2048
        if len(requests) % 2:
            message, finish = tool_message, "tool_calls"
        else:
            assert body["messages"][-2] == tool_message
            assert body["messages"][-1]["role"] == "tool"
            assert body["messages"][-1]["tool_call_id"] == "story-1"
            message, finish = {"role": "assistant", "content": "Done."}, "stop"
        return httpx.Response(
            200,
            json={
                "model": "test-model",
                "choices": [{"message": message, "finish_reason": finish}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            },
        )

    def make(settings: LlmSettings) -> ChatCompletionsLlm:
        return ChatCompletionsLlm(
            settings,
            env={"OPENROUTER_API_KEY": "test-key"},
            transport=httpx.MockTransport(handle),
        )

    monkeypatch.setattr(factory, "ChatCompletionsLlm", make)
    out = tmp_path / provider
    result = runner.invoke(
        cli.app,
        [
            "narrate",
            "--prompt",
            "A world",
            "--out",
            str(out),
            "--provider",
            provider,
            "--model",
            "test-model",
            "--max-tokens",
            "2048",
        ],
    )
    assert result.exit_code == 0, result.output
    tree = Tree.load(out / "tree.json")
    assert tree.node(tree.root).story == "A complete world."
    assert tree.node(tree.root).status == "told"
    assert f"Using {provider}:test-model" in result.output
    assert "Tokens in: 20, cached: 0, out: 10" in result.output
    assert "test-key" not in (out / "log.jsonl").read_text()
    assert json.loads((out / "log.jsonl").read_text().splitlines()[0])["max_tokens"] == 2048
    assert len(requests) == 2
