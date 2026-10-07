import pytest

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
