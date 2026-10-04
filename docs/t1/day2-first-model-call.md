# Day 2 — First model call

## Goal

The goal of this experiment was to prepare a VM-based development environment for `finance-lab-agent` and prove that I could make a real LLM request with synthetic finance data.

During the VM setup work, I tried Multipass, Lima, and VirtualBox. Lima gave me the best experience, so `linux-lab-lima` is now my default local Linux environment.

## Provider decision

Initially I planned to use Yandex AI Studio because the project will use Yandex Cloud. I changed this assumption instead of coupling the model provider to the cloud provider.

I tested OpenAI's **Sign in with ChatGPT** flow because, where possible, I want model usage and quota/cost responsibility to belong to the user rather than requiring the application owner to provide and pay for a shared API key.

This does not remove the application's responsibility for authorization, safe tool execution, rate limits, and other controls.

## What worked

I successfully:

- authenticated with my ChatGPT account using OAuth;
- enabled ChatGPT usage sharing for the application;
- discovered the models available to my account;
- found `GPT-5.6-Sol`;
- sent a real model request using synthetic finance data;
- received a successful response without providing an OpenAI API key.

Synthetic input:

- Housing: 50,000 RUB
- Food: 25,000 RUB
- Transport: 10,000 RUB

The model was asked which category had the largest allocation.

Result:

> Housing has the largest allocation at 50,000 RUB.

Only synthetic data was used because real financial data is unnecessary for this integration experiment and would create an avoidable privacy risk.

## Problems and debugging

Several failures happened during the experiment:

1. Python virtual environment creation failed because Ubuntu did not have the `python3.12-venv` package installed.
2. OpenAI's Paste Perfect example failed during the macOS native build because of a `codesign`/native packaging problem. This was unrelated to ChatGPT OAuth, so I bypassed the native paste component instead of debugging an irrelevant subsystem.
3. The initial JavaScript smoke-test file became corrupted while being pasted through the terminal. I switched to transferring the script as a file instead.
4. The Electron smoke test appeared to hang. By adding checkpoints, I found that execution stopped at `app.whenReady()`. The problem was the way I used top-level `await`; moving the execution into `app.whenReady().then(...)` fixed it.

The main debugging lesson was to identify the failing layer before changing the system. A failure that looked like an OpenAI integration problem was actually, at different times, an OS package problem, a native packaging problem, malformed JavaScript, and an Electron lifecycle problem.

## Important limitation

The successful model inference did **not** run inside Lima yet.

Lima currently contains the Python development environment for `finance-lab-agent`, while the successful ChatGPT OAuth and model call ran on macOS using OpenAI's local reference integration.

This experiment proves that the local/open-source Sign in with ChatGPT approach works for my account. It does not yet prove that this will be the final authentication architecture for a remotely hosted cloud service.

## Adapter test evidence — 2026-10-04

Continued inside Lima using Python 3.12.3 and pytest 9.1.1. Anton added the prompt and timeout assertions to the fake transport; Codex added the initial happy-path test and the two exception tests. Anton then changed the timeout fake to raise Python's `TimeoutError`, observed one failing test, and added `try/except` to convert it into `ModelTimeoutError`. The tests passed after this change. Codex completed generic-error conversion and input validation, with tests for original exception causes, preservation of existing model errors, and rejection of invalid inputs before the transport is called.

Verified behavior:

- `complete()` returns the transport response and forwards the valid prompt and explicit timeout unchanged.
- Blank prompts and zero, negative, infinite, or NaN timeout values raise `ValueError` before the transport is called.
- A transport `TimeoutError` is converted into `ModelTimeoutError`, preserving its message and original cause.
- A transport `RuntimeError` is converted into `ModelError`, preserving its message and original cause.
- Existing `ModelError` and `ModelTimeoutError` instances pass through unchanged.

Run from the repository root:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Result: **12 passed in 0.01s**. These tests use synthetic strings and fake transports, with no credentials, network requests, or sleeps. The earlier macOS model experiment was not rerun.

The adapter passes the timeout to its transport; it does not enforce a deadline. The timeout-conversion test uses Python's built-in `TimeoutError`. A real provider's timeout classification and enforcement remain unverified.

## Next step

The broader T1.1 Yandex task in issue #1 remains outstanding and should stay open. A real provider transport and verification of its timeout behavior remain outstanding.

Sign in with ChatGPT should remain a serious provider/authentication option, but I should not force the whole architecture around it before comparing the complexity with conventional model APIs.

## Time

Planned: approximately 1h15.

Actual: approximately 1h30.

## What I learned

Before this experiment, I had not worked through the complete path from user authentication to model discovery and a real model response using a ChatGPT account instead of an API key.

I also practiced diagnosing failures by isolating the failing layer rather than assuming that the most visible external dependency was responsible.
