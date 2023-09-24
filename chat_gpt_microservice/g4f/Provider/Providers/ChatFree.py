import json
import os
from typing import get_type_hints

import requests

url = "https://v.chatfree.cc"
model = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
supports_stream = False
needs_auth = False


def _create_completion(model: str, messages: list, stream: bool, **kwargs):
    headers = {
        "authority": "chat.dfehub.com",
        "accept": "*/*",
        "accept-language": "en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3",
        "content-type": "application/json",
        "origin": "https://v.chatfree.cc",
        "referer": "https://v.chatfree.cc/",
        "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    json_data = {
        "messages": messages,
        "stream": True,
        "model": model,
        "temperature": 0.5,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_p": 1,
    }

    response = requests.post(
        "https://v.chatfree.cc/api/openai/v1/chat/completions",
        headers=headers,
        json=json_data,
    )

    for chunk in response.iter_lines():
        if b"content" in chunk:
            data = json.loads(chunk.decode().split("data: ")[1])
            yield (data["choices"][0]["delta"]["content"])


params = f"g4f.Providers.{os.path.basename(__file__)[:-3]} supports: " + "(%s)" % ", ".join(
    [
        f"{name}: {get_type_hints(_create_completion)[name].__name__}"
        for name in _create_completion.__code__.co_varnames[: _create_completion.__code__.co_argcount]
    ]
)
