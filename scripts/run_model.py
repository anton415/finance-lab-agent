import os
from time import perf_counter

from finance_lab_agent.model import ModelAdapter
from finance_lab_agent.yandex import yandex_transport


def main():
    adapter = ModelAdapter(yandex_transport)
    prompt = (
        "Synthetic budget in RUB: Housing 50000, Food 60000, Transport 100000. "
        "Which category has the largest allocation? Answer in one sentence."
    )

    print("Model:", os.environ["YANDEX_MODEL_URI"].rsplit("/", 1)[-1])
    started = perf_counter()
    print(adapter.complete(prompt, 30.0))
    print(f"Elapsed: {perf_counter() - started:.2f} seconds")


if __name__ == "__main__":
    main()
