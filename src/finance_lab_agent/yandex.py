import os

import httpx


URL = "https://ai.api.cloud.yandex.net/v1/chat/completions"


def yandex_transport(prompt: str, timeout_seconds: float) -> str:
    api_key = os.environ["YANDEX_API_KEY"]
    model_uri = os.environ["YANDEX_MODEL_URI"]
    folder_id = model_uri.removeprefix("gpt://").split("/", 1)[0]

    headers = {
        "Authorization": f"Api-Key {api_key}",
        "OpenAI-Project": folder_id,
    }
    payload = {
        "model": model_uri,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 128,
        "temperature": 0,
    }


    try:
        response = httpx.post(
            URL, headers=headers, json=payload, timeout=timeout_seconds
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except httpx.TimeoutException as error:
        raise TimeoutError("Yandex request timed out") from error
