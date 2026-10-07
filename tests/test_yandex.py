import json

import httpx
import pytest

from finance_lab_agent import yandex
from finance_lab_agent.model import ModelAdapter, ModelError, ModelTimeoutError


@pytest.fixture(autouse=True)
def synthetic_yandex_settings(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "synthetic-test-key")
    monkeypatch.setenv("YANDEX_MODEL_URI", "gpt://test-folder/yandexgpt-5.1")


def test_yandex_request_and_response(monkeypatch):
    def handle(request):
        assert request.method == "POST"
        assert str(request.url) == "https://ai.api.cloud.yandex.net/v1/chat/completions"
        assert request.headers["Authorization"] == "Api-Key synthetic-test-key"
        assert request.headers["OpenAI-Project"] == "test-folder"
        assert request.headers["Content-Type"] == "application/json"
        body = json.loads(request.content)
        assert body["model"] == "gpt://test-folder/yandexgpt-5.1"
        assert body["messages"] == [{"role": "user", "content": "Synthetic budget prompt"}]
        assert body["max_tokens"] == 128
        assert request.extensions["timeout"] == {
            "connect": 5.0, "read": 5.0, "write": 5.0, "pool": 5.0
        }
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Housing is largest."}}]},
        )

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        monkeypatch.setattr(yandex.httpx, "post", client.post)
        result = ModelAdapter(yandex.yandex_transport).complete(
            "Synthetic budget prompt", 5.0
        )

    assert result == "Housing is largest."


def test_yandex_http_error_reaches_adapter(monkeypatch):
    def handle(request):
        return httpx.Response(503, json={"error": "synthetic provider failure"})

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        monkeypatch.setattr(yandex.httpx, "post", client.post)
        with pytest.raises(ModelError) as caught:
            ModelAdapter(yandex.yandex_transport).complete("Synthetic prompt", 5.0)

    assert type(caught.value) is ModelError
    assert isinstance(caught.value.__cause__, httpx.HTTPStatusError)
    assert caught.value.__cause__.response.status_code == 503


def test_yandex_timeout_reaches_adapter(monkeypatch):
    def handle(request):
        raise httpx.ReadTimeout("synthetic read timeout", request=request)

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        monkeypatch.setattr(yandex.httpx, "post", client.post)
        with pytest.raises(ModelTimeoutError, match="Yandex request timed out") as caught:
            ModelAdapter(yandex.yandex_transport).complete("Synthetic prompt", 5.0)

    assert isinstance(caught.value.__cause__, TimeoutError)
    assert isinstance(caught.value.__cause__.__cause__, httpx.ReadTimeout)


@pytest.mark.parametrize(
    "message",
    [
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "synthetic-call-1",
                    "type": "function",
                    "function": {
                        "name": "get_budget",
                        "arguments": '{"month": "2026-10"}',
                    },
                },
            ],
        },
        {"role": "assistant", "content": "Please specify a month."},
    ],
)
def test_budget_tool_request_preserves_complete_message(message, monkeypatch):
    def handle(request):
        assert request.method == "POST"
        assert str(request.url) == "https://ai.api.cloud.yandex.net/v1/chat/completions"
        assert request.headers["Authorization"] == "Api-Key synthetic-test-key"
        assert request.headers["OpenAI-Project"] == "test-folder"
        assert json.loads(request.content) == {
            "model": "gpt://test-folder/yandexgpt-5.1",
            "messages": [{"role": "user", "content": "Read my synthetic October budget."}],
            "max_tokens": 128,
            "temperature": 0,
            "tools": [yandex.GET_BUDGET_TOOL],
            "tool_choice": "auto",
        }
        assert request.extensions["timeout"] == {
            "connect": 5.0, "read": 5.0, "write": 5.0, "pool": 5.0
        }
        return httpx.Response(200, json={"choices": [{"message": message}]})

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        monkeypatch.setattr(yandex.httpx, "post", client.post)
        result = yandex.request_budget_tool("Read my synthetic October budget.", 5.0)

    assert result == message


def test_budget_tool_request_rejects_http_error(monkeypatch):
    def handle(request):
        return httpx.Response(503, json={"error": "synthetic provider failure"})

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        monkeypatch.setattr(yandex.httpx, "post", client.post)
        with pytest.raises(httpx.HTTPStatusError) as caught:
            yandex.request_budget_tool("Synthetic prompt", 5.0)

    assert caught.value.response.status_code == 503


def test_budget_tool_request_converts_timeout(monkeypatch):
    def handle(request):
        raise httpx.ReadTimeout("synthetic read timeout", request=request)

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        monkeypatch.setattr(yandex.httpx, "post", client.post)
        with pytest.raises(TimeoutError, match="Yandex request timed out") as caught:
            yandex.request_budget_tool("Synthetic prompt", 5.0)

    assert isinstance(caught.value.__cause__, httpx.ReadTimeout)
