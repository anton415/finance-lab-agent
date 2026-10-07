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


def invoke_get_budget(arguments: dict) -> dict:
    if (
        isinstance(arguments, dict)
        and set(arguments) == {"month"}
        and isinstance(arguments["month"], str)
    ):
        return get_budget(arguments["month"])
    else:
        raise ValueError(
            "arguments must be a dictionary containing only a string 'month' field"
        )
