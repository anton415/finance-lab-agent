import json
import os
from time import perf_counter

import httpx

from finance_lab_agent.budget import execute_tool_call
from finance_lab_agent.yandex import request_budget_tool


def main() -> int:
    prompt = "Use get_budget to read the synthetic budget for 2026-10."
    try:
        print("Model:", os.environ["YANDEX_MODEL_URI"].rsplit("/", 1)[-1])
        print("Prompt:", prompt)
        started = perf_counter()
        message = request_budget_tool(prompt, 30.0)
    except KeyError as error:
        if error.args[0] in {"YANDEX_API_KEY", "YANDEX_MODEL_URI"}:
            print("Missing environment setting:", error.args[0])
        else:
            print("Unexpected Yandex response structure.")
        return 1
    except (IndexError, TypeError, ValueError):
        print("Unexpected Yandex response structure.")
        return 1
    except TimeoutError:
        print("Yandex request timed out.")
        return 1
    except httpx.HTTPStatusError as error:
        print("Yandex HTTP error:", error.response.status_code)
        return 1
    except httpx.RequestError:
        print("Yandex connection failed.")
        return 1

    print(f"Request elapsed: {perf_counter() - started:.2f} seconds")
    if not isinstance(message, dict):
        print("Unexpected Yandex response structure.")
        return 1

    calls = message.get("tool_calls")
    if calls is None or calls == []:
        print("No tool call returned; no budget function executed.")
        print("Model text:", json.dumps(message.get("content"), ensure_ascii=False))
        return 2
    if not isinstance(calls, list) or len(calls) != 1:
        print("Tool call rejected: expected exactly one function call.")
        return 1

    call = calls[0]
    if not isinstance(call, dict) or call.get("type") != "function":
        print("Tool call rejected: expected a function call.")
        return 1
    function = call.get("function")
    if not isinstance(function, dict):
        print("Tool call rejected: missing function details.")
        return 1

    try:
        result = execute_tool_call(function.get("name"), function.get("arguments"))
    except ValueError as error:
        print("Tool call rejected:", error)
        return 1

    print("Tool:", function["name"])
    print("Validated arguments:", json.dumps({"month": result["month"]}))
    print("Tool result:", json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
