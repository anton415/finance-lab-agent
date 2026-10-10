import json
from pathlib import Path
import runpy

import httpx
import pytest

from finance_lab_agent import budget, yandex


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/run_budget_tool.py"


def tool_call(name="get_budget", arguments='{"month": "2026-10"}'):
    return {
        "id": "synthetic-call-1",
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }


@pytest.fixture
def run_with_response(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "synthetic-test-key")
    monkeypatch.setenv("YANDEX_MODEL_URI", "gpt://test-folder/yandexgpt-5.1")

    def run(message, status=200):
        requests = []

        def handle(request):
            requests.append(request)
            return httpx.Response(status, json={"choices": [{"message": message}]})

        with httpx.Client(transport=httpx.MockTransport(handle)) as client:
            monkeypatch.setattr(yandex.httpx, "post", client.post)
            with pytest.raises(SystemExit) as stopped:
                runpy.run_path(str(SCRIPT), run_name="__main__")
        assert len(requests) == 1
        return stopped.value.code, json.loads(requests[0].content)

    return run


def test_runner_executes_one_validated_budget_call(run_with_response, capsys):
    status, request = run_with_response(
        {"role": "assistant", "content": None, "tool_calls": [tool_call()]}
    )
    assert status == 0
    assert request["tools"] == [budget.GET_BUDGET_TOOL]
    assert request["tool_choice"] == "auto"
    assert request["messages"] == [
        {
            "role": "user",
            "content": "Use get_budget to read the synthetic budget for 2026-10.",
        }
    ]
    output = capsys.readouterr().out
    result = json.loads(output.split("Tool result: ", 1)[1])
    assert result == {
        "month": "2026-10",
        "currency": "RUB",
        "allocations": {"Housing": 50000, "Food": 25000, "Transport": 10000},
    }


def test_runner_reports_text_only_without_executing_budget(
    run_with_response, monkeypatch, capsys
):
    def unexpected_budget(month):
        pytest.fail("No tool call was requested")

    monkeypatch.setattr(budget, "get_budget", unexpected_budget)
    status, _ = run_with_response(
        {"role": "assistant", "content": "Synthetic text-only response."}
    )
    assert status == 2
    output = capsys.readouterr().out
    assert "No tool call returned" in output
    assert "Synthetic text-only response." in output


@pytest.mark.parametrize(
    "message",
    [
        None,
        {"tool_calls": {}},
        {"tool_calls": [tool_call(), tool_call()]},
        {"tool_calls": [{"type": "custom", "function": {}}]},
        {"tool_calls": [{"type": "function", "function": None}]},
        {"tool_calls": [tool_call(name="delete_budget")]},
        {"tool_calls": [tool_call(arguments="not JSON")]},
        {"tool_calls": [tool_call(arguments="{}")]},
    ],
)
def test_runner_rejects_invalid_call_before_budget_execution(
    message, run_with_response, monkeypatch
):
    def unexpected_budget(month):
        pytest.fail("Invalid model response must not execute the budget function")

    monkeypatch.setattr(budget, "get_budget", unexpected_budget)
    status, _ = run_with_response(message)
    assert status == 1


def test_runner_reports_http_failure_without_provider_details(
    run_with_response, capsys
):
    status, _ = run_with_response(None, status=503)
    assert status == 1
    output = capsys.readouterr().out
    assert "Yandex HTTP error: 503" in output
    assert "synthetic-test-key" not in output
    assert "test-folder" not in output
