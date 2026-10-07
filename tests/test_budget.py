import pytest

from finance_lab_agent import budget as budget_module
from finance_lab_agent.budget import get_budget


def test_get_budget_returns_synthetic_october_budget():
    result = get_budget("2026-10")

    assert result == {
        "month": "2026-10",
        "currency": "RUB",
        "allocations": {
            "Housing": 50000,
            "Food": 25000,
            "Transport": 10000,
        },
    }


@pytest.mark.parametrize("month", ["2026-11", "not-a-month", None])
def test_get_budget_rejects_unavailable_or_invalid_month(month):
    with pytest.raises(ValueError, match="Synthetic budget is unavailable"):
        get_budget(month)


def test_changing_returned_allocations_does_not_change_later_results():
    budget = get_budget("2026-10")
    budget["allocations"]["Housing"] = 0

    assert get_budget("2026-10")["allocations"]["Housing"] == 50000


def test_invoke_get_budget_forwards_month_and_returns_result(monkeypatch):
    calls = []
    expected = {"month": "2026-11", "currency": "RUB", "allocations": {}}

    def fake_get_budget(month):
        calls.append(month)
        return expected

    monkeypatch.setattr(budget_module, "get_budget", fake_get_budget)

    result = budget_module.invoke_get_budget({"month": "2026-11"})

    assert calls == ["2026-11"]
    assert result is expected


@pytest.mark.parametrize(
    "arguments",
    [
        None,
        ["month"],
        "2026-10",
        {},
        {"unexpected": "2026-10"},
        {"month": "2026-10", "extra": True},
        {"month": None},
        {"month": 202610},
    ],
)
def test_invoke_get_budget_rejects_invalid_arguments_before_calling_budget(
    arguments, monkeypatch
):
    def unexpected_get_budget(month):
        pytest.fail("get_budget must not run for invalid arguments")

    monkeypatch.setattr(budget_module, "get_budget", unexpected_get_budget)

    with pytest.raises(ValueError, match="arguments must be a dictionary"):
        budget_module.invoke_get_budget(arguments)


def test_invoke_get_budget_preserves_unavailable_month_error():
    with pytest.raises(ValueError, match="Synthetic budget is unavailable"):
        budget_module.invoke_get_budget({"month": "2026-11"})
