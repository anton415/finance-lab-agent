# finance-lab-agent

A small Python learning project for a real model call with synthetic finance data. The current transport uses Yandex AI Studio Chat Completions through `ModelAdapter`.

## Setup

From the repository root inside the Linux VM, with Python 3.12 and venv support installed:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The verified environment used Python 3.12.3, HTTPX 0.28.1, and pytest 9.1.1. Dependencies are declared in `requirements.txt`; these observations are not a lockfile.

## Offline tests

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Tests use fake transports or HTTPX MockTransport with synthetic credentials. They do not call a live model.

## Configure a real request

Use Bash in your own VM account. You need a Yandex AI Studio API key with model access and the associated folder ID. [Yandex's basic-request documentation](https://aistudio.yandex.ru/en/docs/ai-studio/operations/generation/completions-basic) describes the required access.

Run this command by itself, paste the secret at the prompt, and press Enter. Input is hidden and is not a shell command:

```bash
read -r -s -p "Yandex API key: " YANDEX_API_KEY
```

Then export the variables. Replace `<folder_ID>` with your actual folder ID in your terminal, not in this file:

```bash
printf '\n'
export YANDEX_API_KEY
export YANDEX_MODEL_URI='gpt://<folder_ID>/yandexgpt-5.1'
```

Keep using that terminal: these environment variables belong to its session. The program does not automatically load `.env` files. Keep credentials out of source files, command arguments, screenshots, and Git.

## Run the synthetic example

This sends one real request, which can consume your provider quota or balance:

```bash
PYTHONPATH=src .venv/bin/python scripts/run_model.py
```

The input is Housing 50,000 RUB, Food 60,000 RUB, and Transport 100,000 RUB. The expected largest category is Transport; exact wording and elapsed time can vary. The request uses `max_tokens=128` and `temperature=0`.

The script passes `30.0` to HTTPX for its connect/read/write/pool timeout settings. This is not a total wall-clock deadline: HTTPX read/write limits apply while waiting for individual chunks. See [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/).

## Read-only budget tool experiment

The tool input is a JSON object with exactly one required string field, for example
`{"month": "2026-10"}`. Only the synthetic October 2026 fixture is available.

The tool result has exactly these fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `month` | string | Requested fixture month, `2026-10`. |
| `currency` | string | `RUB`. |
| `allocations` | object | Category names mapped to integer RUB amounts: Housing 50000, Food 25000, Transport 10000. |

Use the same VM terminal and environment settings as the real-request setup above:

```bash
PYTHONPATH=src .venv/bin/python scripts/run_budget_tool.py
```

This makes one real model request with the budget tool description. It executes at
most one validated `get_budget` call locally and prints the synthetic result.
The model prompt contains the requested month, not the allocation amounts.
The run ends after the local result; it does not send a second model request.
There are no retries, writes, or database access.

Exit status `0` means a validated tool call succeeded; `2` means the model returned
no tool call; `1` means a request, response, or validation failure. A text-only
response is reported without executing the budget function. HTTP failures print
the status code without credentials or the provider response body.

The runner is tested offline with fake HTTP responses. A live YandexGPT 5.1 request
on 2026-10-07 returned a budget tool call, which the runner validated and executed locally. See the
[T1.2 evidence](docs/t1/t1-2-read-only-budget-tool.md) for the observed result and remaining learning checks.

## Request path and errors

`scripts/run_model.py` calls `ModelAdapter.complete()`, which validates the inputs and calls `yandex_transport`. The transport loads settings from the environment, builds the authentication headers and JSON body, and posts to Yandex. It checks the HTTP status and returns the first message's text.

HTTPX timeouts become Python `TimeoutError`, then `ModelTimeoutError` at the adapter boundary. HTTP status failures become `ModelError`, with the original exception preserved as the cause. No retries or agent framework are included.

## Evidence

- [First Python-to-Yandex call](docs/t1/day2-yandex-model-call.md): successful real request in Lima on 2026-10-06, plus offline verification.
- [Earlier ChatGPT sign-in experiment and adapter work](docs/t1/day2-first-model-call.md): historical macOS experiment and the initial adapter tests.

Related to [issue #1](https://github.com/anton415/finance-lab-agent/issues/1). A successful run is not a claim that every T1 learning criterion is complete.
