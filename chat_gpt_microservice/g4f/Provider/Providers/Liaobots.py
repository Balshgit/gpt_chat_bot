import os

import requests

from ...typing import get_type_hints

url = "https://liaobots.com"
model = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"]
supports_stream = True
needs_auth = True
working = False

models = {
    "gpt-4": {"id": "gpt-4", "name": "GPT-4", "maxLength": 24000, "tokenLimit": 8000},
    "gpt-3.5-turbo": {
        "id": "gpt-3.5-turbo",
        "name": "GPT-3.5",
        "maxLength": 12000,
        "tokenLimit": 4000,
    },
    "gpt-3.5-turbo-16k": {
        "id": "gpt-3.5-turbo-16k",
        "name": "GPT-3.5-16k",
        "maxLength": 48000,
        "tokenLimit": 16000,
    },
}


def _create_completion(model: str, messages: list, stream: bool, chatId: str, **kwargs):
    print(kwargs)

    headers = {
        "authority": "liaobots.com",
        "content-type": "application/json",
        "origin": "https://liaobots.com",
        "referer": "https://liaobots.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "x-auth-code": "qlcUMVn1KLMhd",
    }

    json_data = {
        "conversationId": chatId,
        "model": models[model],
        "messages": messages,
        "key": "",
        "prompt": "You are ChatGPT, a large language model trained by OpenAI. Follow the user's instructions carefully. Respond using markdown.",
    }

    response = requests.post("https://liaobots.com/api/chat", headers=headers, json=json_data, stream=True)

    for token in response.iter_content(chunk_size=2046):
        yield (token.decode("utf-8"))


params = f"g4f.Providers.{os.path.basename(__file__)[:-3]} supports: " + "(%s)" % ", ".join(
    [
        f"{name}: {get_type_hints(_create_completion)[name].__name__}"
        for name in _create_completion.__code__.co_varnames[: _create_completion.__code__.co_argcount]
    ]
)
