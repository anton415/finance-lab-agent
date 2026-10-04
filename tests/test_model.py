import pytest

from finance_lab_agent.model import ModelAdapter, ModelError, ModelTimeoutError


def fake_transport(prompt, timeout_seconds):
    assert prompt == "test prompt"
    assert timeout_seconds == 5.0
    return "fake response"


def test_complete_returns_transport_response():
    adapter = ModelAdapter(fake_transport)

    result = adapter.complete("test prompt", 5.0)

    assert result == "fake response"


def test_complete_converts_timeout_error():
    error = TimeoutError("model request timed out")

    def timeout_transport(prompt, timeout_seconds):
        raise error

    adapter = ModelAdapter(timeout_transport)

    with pytest.raises(ModelTimeoutError, match="model request timed out") as caught:
        adapter.complete("test prompt", 5.0)

    assert caught.value.__cause__ is error


def test_complete_converts_provider_error():
    error = RuntimeError("model request failed")

    def failing_transport(prompt, timeout_seconds):
        raise error

    adapter = ModelAdapter(failing_transport)

    with pytest.raises(ModelError, match="model request failed") as caught:
        adapter.complete("test prompt", 5.0)

    assert type(caught.value) is ModelError
    assert caught.value.__cause__ is error


@pytest.mark.parametrize("error", [ModelError("failed"), ModelTimeoutError("timed out")])
def test_complete_preserves_existing_model_error(error):
    def failing_transport(prompt, timeout_seconds):
        raise error

    adapter = ModelAdapter(failing_transport)

    with pytest.raises(type(error)) as caught:
        adapter.complete("test prompt", 5.0)

    assert caught.value is error
