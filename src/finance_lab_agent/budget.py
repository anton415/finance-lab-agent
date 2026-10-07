def get_budget(month: str) -> dict:
    if "2026-10" == month:
        return {
            "month": month,
            "currency": "RUB",
            "allocations": {
                "Housing": 50000,
                "Food": 25000,
                "Transport": 10000,
            },
        }
    else:
        raise ValueError("Synthetic budget is unavailable for this month")
