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


def test_complete_propagates_timeout():
    def timeout_transport(prompt, timeout_seconds):
        raise ModelTimeoutError("model request timed out")

    adapter = ModelAdapter(timeout_transport)

    with pytest.raises(ModelTimeoutError, match="model request timed out"):
        adapter.complete("test prompt", 5.0)


def test_complete_propagates_model_error():
    def failing_transport(prompt, timeout_seconds):
        raise ModelError("model request failed")

    adapter = ModelAdapter(failing_transport)

    with pytest.raises(ModelError, match="model request failed"):
        adapter.complete("test prompt", 5.0)
