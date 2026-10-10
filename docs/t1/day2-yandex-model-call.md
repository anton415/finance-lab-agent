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
- At the time of this real-request session, fresh-checkout setup and second-host execution were not tested. The fresh-environment check below records later progress; second-host execution remains untested.
- Issue #1 remains open; no GitHub issue or project state was changed. The earlier ChatGPT experiment remains historical evidence, not a second provider implementation in this code.

## Fresh Python environment check — 2026-10-10

- Source revision: `8528dcd684baad3b3a3313374553937bbe7c0590`.
- Codex extracted only committed files with `git archive` into a temporary directory in the existing Lima VM. No previous virtual environment or `.env` file was copied.
- Anton ran the documented setup and offline tests himself using the supplied commands:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Observed result: dependency installation succeeded; **57 passed in 0.05s**.
Codex read the app terminal, checked the installed versions, and confirmed that all copied project files still matched the source revision.
The new environment used Python 3.12.3, HTTPX 0.28.1, and pytest 9.1.1.

This verifies the documented Python setup and offline suite from committed source in a fresh virtual environment. It reused the existing VM, installed Python/venv support, and pip cache; it does not establish fresh-VM provisioning or second-computer reproduction. The test run made no live model request. Dependencies remain unpinned; the observed versions are not a lockfile.

This was a guided setup check, not an independent assessment of the request path or tool contract. Issue #1 remains open.

Planned time: approximately 5–10 minutes. Actual active time: 5 minutes (reported by Anton).

## Human-authored prompt change and live rerun — 2026-10-10

Base revision: `f4d182845e55c5205e223859f7757b0a94366a44`, with the accompanying prompt and README changes.

After a guided request-path explanation, Anton wrote this modified synthetic prompt himself:

> Synthetic budget in RUB: Housing 50000, Food 60000, Transport 10000. Which category has the largest allocation? Answer in one sentence.

Codex applied Anton's exact text to `scripts/run_model.py`, updated the matching README example, and checked Python syntax. Anton ran the script in the existing VM:

```bash
PYTHONPATH=src .venv/bin/python scripts/run_model.py
```

The first attempt stopped at a missing `YANDEX_MODEL_URI` environment setting. After restoring it, the next attempt stopped at a missing `YANDEX_API_KEY`, which the adapter wrapped as `ModelError`. Both failures occurred before an HTTP request. With supplied instructions, Anton restored the model setting and exported the API key through a hidden terminal prompt, then reran the script.

Codex read this successful result directly from the app terminal:

```text
Model: yandexgpt-5.1
The category with the largest allocation is Food, with 60000 RUB.
Elapsed: 1.26 seconds
```

The response identifies the largest allocation in Anton's modified input. Elapsed time covers the adapter call; no separate numeric exit status, token usage, or cost was captured. The synthetic budget tool fixture was not changed. No credential values, private folder IDs, or raw terminal logs are included here.

With guidance, Anton described the adapter as checking and forwarding inputs, identified `yandex_transport` as sending the request to Yandex, identified HTTPX as enforcing network timeouts, and explained that Python reads the exported API key through `os.environ`. He also correctly identified the injected fake transport as the function called in the fake example. These were guided explanations, and the setup-error recovery used supplied commands; this does not establish independent end-to-end diagnosis. Anton authored the prompt modification; Codex performed the file edit. Issue #1 remains open.

No separate planned duration was established for this guided review and rerun. Actual active time: 15 minutes (reported by Anton), excluding the earlier 5-minute fresh-environment setup check.

## Follow-up explanation checks and direct prompt edit — 2026-10-10

Execution source: `e46ffee744661117654e54ec048908be61c520fd`, plus Anton's
one-line prompt edit below. Its committed tree matches the merged baseline
`81a86b24d94097e36c00a5b7a1a921fc7adf1445`.

### Explanation checks

With the source available for reference, Anton gave these correct explanations:

- The API key is read from `os.environ["YANDEX_API_KEY"]`, placed in the
  `Authorization` header with the `Api-Key` scheme, and used in a POST request
  to `https://ai.api.cloud.yandex.net/v1/chat/completions`.
- HTTP 503 is detected by `response.raise_for_status()`. The adapter's generic
  exception handler converts the resulting `httpx.HTTPStatusError` into
  `ModelError`; `from error` retains the original exception as the cause.
- The timeout path is `httpx.ReadTimeout` → `TimeoutError` → `ModelTimeoutError`.
- The adapter calls its injected transport: the test's `fake_transport` returns
  a fixed local response, while `yandex_transport` sends the HTTP request.
- HTTPX enforces individual network-operation timeouts. A value of `30.0`
  does not guarantee a 30-second deadline for the entire call.

The HTTP 503 explanation used incremental questions and a displayed `raise`
statement. The other answers followed focused questions without a supplied
answer in that attempt. These are source-referenced explanation checks, not
an unaided end-to-end troubleshooting assessment.

### Human edit and observed result

The task was to change one synthetic amount so a different category would be
largest. Anton chose Transport at 100,000 RUB, edited and saved an editing copy
of `scripts/run_model.py` himself, and predicted Transport as the result.
Codex verified that the only change was `Transport 10000` → `Transport 100000`
and copied the exact saved file into the VM after checking the original hash.

Anton reported that the app terminal was unavailable and explicitly asked
Codex to run the documented command:

```bash
PYTHONPATH=src .venv/bin/python scripts/run_model.py
```

The first attempt exited 1 before an API call because `YANDEX_MODEL_URI` was
missing. Neither required Yandex setting was present in that execution shell.
Anton supplied his existing API key through a hidden local prompt; Codex
restored the model setting and saved both settings in an owner-only VM file
outside Git. No replacement key was created. After loading those settings into
the process environment, Codex reran the command once and observed:

```text
Model: yandexgpt-5.1
The category with the largest allocation is Transport.
Elapsed: 0.88 seconds
Exit status: 0
```

The result matches Anton's chosen input and prediction. Codex checked Python
syntax and the whitespace diff and updated the README example. The full test
suite was not rerun for this prompt-only change. The read-only budget fixture
remains unchanged. No secrets, private identifiers, or raw terminal logs are
included in this record; token usage and cost were not captured.

### Time and acceptance

- Planned: approximately 5 minutes for the modification and rerun.
- Actual: 30 active minutes, reported by Anton, including settings recovery and
  excluding breaks and waiting.
- The request-path explanation checks and human-chosen file modification have
  evidence. Configuration recovery, file transfer, and command execution were
  assisted; the live rerun must not be described as independently performed by Anton.
- T1.1 is ready for final evidence and human acceptance review with those limits
  explicit. Issue #1 remains open; this note does not change its GitHub state.
