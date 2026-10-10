# Day 2 follow-up: first Python-to-Yandex model call

- Date: 2026-10-06.
- Related issue: https://github.com/anton415/finance-lab-agent/issues/1
- Base commit: `f5994e6aa69f6ffc080c158e8a256b8c9e705fbd`, followed by the Yandex transport, tests, launcher, and documentation accompanying this record.
- Environment: existing Lima Linux VM; Python 3.12.3, HTTPX 0.28.1, pytest 9.1.1.
- Provider/API: Yandex AI Studio, OpenAI-compatible Chat Completions, `POST https://ai.api.cloud.yandex.net/v1/chat/completions`.
- Requested model: YandexGPT Pro 5.1, `gpt://<folder_ID>/yandexgpt-5.1`. The private folder ID is omitted.
- Authentication: API key supplied in the VM shell environment; no credential value is recorded.
- Input: synthetic budget only; Housing 50,000 RUB, Food 25,000 RUB, Transport 10,000 RUB.
- Settings: `max_tokens=128`, `temperature=0`, `timeout_seconds=30.0`.

## Real-run result

Anton ran the supplied Python heredoc in the same VM shell where he exported `YANDEX_API_KEY` and `YANDEX_MODEL_URI`. His screenshot shows:

```text
Model: yandexgpt-5.1
The category with the largest allocation is Housing.
Elapsed: 0.52 seconds
```

The answer correctly identifies the largest synthetic allocation. The shell prompt returned without a traceback; a separate numeric exit-status check was not captured. The elapsed value measures the call through the adapter using `perf_counter`, not Python startup time.

Evidence source: Anton's terminal screenshot. Codex reviewed the source and this output but did not independently repeat the paid request. The screenshot itself is not included because it contains account and local-environment details.

## Command and reproduction

The exact request path used in the demonstrated command was:

```bash
PYTHONPATH=src .venv/bin/python - <<'PY'
import os
from time import perf_counter
from finance_lab_agent.model import ModelAdapter
from finance_lab_agent.yandex import yandex_transport

adapter = ModelAdapter(yandex_transport)
prompt = (
    "Synthetic budget in RUB: Housing 50000, Food 25000, Transport 10000. "
    "Which category has the largest allocation? Answer in one sentence."
)

print("Model:", os.environ["YANDEX_MODEL_URI"].rsplit("/", 1)[-1])
started = perf_counter()
print(adapter.complete(prompt, 30.0))
print(f"Elapsed: {perf_counter() - started:.2f} seconds")
PY
```

Codex subsequently saved this same request as `scripts/run_model.py`, adding only a `main()` entry point. After the [README setup](../../README.md), it can be repeated with:

```bash
PYTHONPATH=src .venv/bin/python scripts/run_model.py
```

The saved launcher was checked offline, not with an additional paid request.

## Offline verification

Before the real request, Codex ran:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Result: `15 passed in 0.02s`. The suite includes the existing 12 adapter cases and three new HTTPX MockTransport tests covering:

- POST endpoint, authentication/project headers, JSON input, output-token limit, explicit HTTPX timeout settings, and answer extraction;
- simulated HTTP 503 reaching the adapter as `ModelError`, preserving its original HTTP-status exception;
- simulated HTTPX read timeout becoming `TimeoutError` and then `ModelTimeoutError`, preserving the exception chain.

Credentials in those tests are synthetic. No tests contact Yandex. These tests verify configuration and error mapping; they do not demonstrate an actual stalled network connection or a live provider outage.

HTTPX has separate connect, read, write, and pool limits. In particular, read/write timeouts concern waiting for chunks, so `30.0` is not a guaranteed overall 30-second deadline. [HTTPX timeout documentation](https://www.python-httpx.org/advanced/timeouts/)

## Human work and assistance

Anton completed account/key setup, loaded the credential privately into his VM shell, and edited the HTTP transport in nano. His first attempt used an arrow for assignment, misspelled `payload`, retained the placeholder exception, and mixed indentation. Codex explained the corrections and supplied the corrected small request/status/parsing block. Anton saved it and executed the real request himself.

Codex prepared the surrounding request settings and timeout translation, added the offline tests, reviewed the saved implementation, and saved the launcher and these notes. This was guided implementation and a demonstrated successful run; independent explanation and modification of the complete request path have not been assessed here.

## Time and limits

- Original Day 2 planned slot: approximately 1 h 15 min; no separate estimate was established for this follow-up.
- Additional actual time for this Yandex follow-up: not recorded yet; requested from Anton. This is separate from the earlier 1 h 30 min ChatGPT experiment and the Linux exercises.
- Token usage and monetary cost were not captured; no estimate is presented as observed cost.
- Fresh-checkout setup and second-host execution were not tested.
- Issue #1 remains open; no GitHub issue or project state was changed. The earlier ChatGPT experiment remains historical evidence, not a second provider implementation in this code.
