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


@pytest.mark.parametrize("prompt", ["", "   "])
def test_complete_rejects_blank_prompt_before_calling_transport(prompt):
    def unexpected_transport(prompt, timeout_seconds):
        pytest.fail("transport must not be called for a blank prompt")

    adapter = ModelAdapter(unexpected_transport)

    with pytest.raises(ValueError, match="prompt must not be empty"):
        adapter.complete(prompt, 5.0)


@pytest.mark.parametrize("timeout_seconds", [0.0, -1.0, float("inf"), float("-inf"), float("nan")])
def test_complete_rejects_invalid_timeout_before_calling_transport(timeout_seconds):
    def unexpected_transport(prompt, timeout_seconds):
        pytest.fail("transport must not be called for an invalid timeout")

    adapter = ModelAdapter(unexpected_transport)

    with pytest.raises(ValueError, match="timeout_seconds must be positive and finite"):
        adapter.complete("test prompt", timeout_seconds)
