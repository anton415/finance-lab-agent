import json

GET_BUDGET_TOOL = {
    "type": "function",
    "function": {
        "name": "get_budget",
        "description": (
            "Read a synthetic monthly budget in RUB. "
            "Only October 2026 is available. Does not change data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "string",
                    "description": "Budget month in YYYY-MM format",
                },
            },
            "required": ["month"],
            "additionalProperties": False,
        },
    },
}


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


def execute_tool_call(name: str, arguments_json: str) -> dict:
    if name != "get_budget":
        raise ValueError("Unsupported tool")
    if not isinstance(arguments_json, str):
        raise ValueError("Tool arguments must be JSON text")
    arguments = json.loads(arguments_json)
    return invoke_get_budget(arguments)
