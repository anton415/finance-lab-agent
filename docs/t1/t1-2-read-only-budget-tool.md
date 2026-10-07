# T1.2: first live read-only budget tool call

- Date: 2026-10-07.
- Related issue: https://github.com/anton415/finance-lab-agent/issues/2.
- Requested model: YandexGPT 5.1, selected through the existing environment setting.
- Evidence source: Anton ran the experiment in his VM terminal; Codex inspected the terminal output directly.
- All budget data is synthetic. Credentials, folder identifiers, local account details, and raw terminal logs are omitted.

## Observed path

1. User intent: read the synthetic budget for October 2026.
2. The runner sent one model request with the `get_budget` tool description and `tool_choice="auto"`.
3. The response requested `get_budget` with arguments that parsed and validated as `{"month": "2026-10"}`.
4. The local Python function returned the deterministic budget below.

The model prompt contained the month and instruction to use the tool, without the allocation amounts.
The runner printed the tool name and normalized validated arguments after successful local execution.
It ended after the local result, without another model request.

## Selected terminal result

```text
Model: yandexgpt-5.1
Prompt: Use get_budget to read the synthetic budget for 2026-10.
Request elapsed: 0.81 seconds
Tool: get_budget
Validated arguments: {"month": "2026-10"}
Tool result: {
  "month": "2026-10",
  "currency": "RUB",
  "allocations": {
    "Housing": 50000,
    "Food": 25000,
    "Transport": 10000
  }
}
```

The shell prompt returned without an error. A separate numeric exit-status check was not captured.
The 0.81 seconds measures the request helper, including response parsing; it is not active learning time.
This verifies one successful function-calling experiment with the selected model and prompt.

## Reproduction and contract

From the repository root in the VM terminal with both Yandex environment settings exported:

```bash
PYTHONPATH=src .venv/bin/python scripts/run_budget_tool.py
```

See the [README contract and setup](../../README.md#read-only-budget-tool-experiment).
The runner executes at most one validated function call. Unknown tools, invalid arguments,
and multiple calls are rejected before budget execution. A text-only response is reported
without invoking the budget function. There are no writes or database access.

Initial attempts stopped locally because the model URI and then the API key were missing
from the terminal environment. Anton restored the settings before the successful request.

## Offline verification

Most recent focused checks from the implementation steps:

- `tests/test_budget.py`: 27 passed; deterministic data, argument validation, JSON parsing, and rejection before budget execution.
- `tests/test_yandex.py`: 7 passed; request contents, complete messages with and without tool calls, HTTP errors, and timeouts.
- `tests/test_run_budget_tool.py`: 11 passed; one-request integration, valid local execution, text-only responses, malformed calls, and HTTP failure.

These focused checks use fake transports and synthetic credentials.

Before committing the combined changes on 2026-10-07, the full offline suite was run with
`PYTHONPATH=src .venv/bin/python -m pytest -q`: **57 passed in 0.04 seconds**.

## Guided manual checks

Anton ran both calls directly in an interactive Python session on 2026-10-07.
Codex inspected the terminal output after each call.

- `execute_tool_call("get_budget", '{"month": "2026-10"}')` returned the expected synthetic October budget.
- `execute_tool_call("get_budget", '{}')` raised `ValueError: arguments must be a dictionary containing only a string 'month' field` in `invoke_get_budget`.

The empty object is valid JSON but lacks the required field. The validator rejected it;
the offline tests additionally verify that invalid arguments never invoke `get_budget`.

These were guided checks: Codex supplied the Python setup and exact commands.
Anton correctly identified that the budget amounts come from `get_budget`.
After clarification about JSON versus read-only behavior, he explained that saving to a
file is a write operation even if the saved values are unchanged. Independent reconstruction
of the invocation and the full contract explanation are still unverified.

## Learning ownership and time

Anton wrote the initial budget function, input validator, tool description, and tool-call
handler with guidance. Codex corrected implementation errors, completed the Yandex request
and runner when asked, and added the tests.

- Planned: 15 minutes was proposed for the initial budget-function exercise; a total T1.2 estimate was not recorded.
- Actual active time: approximately 2 hours, reported by Anton, excluding breaks.
- Independent explanation and manual demonstration: pending.

The live experiment and actual-time record have evidence. Full T1.2 acceptance remains
pending independent human demonstration; this note does not close the issue.
