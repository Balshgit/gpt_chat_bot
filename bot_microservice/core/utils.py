import os
import random
import subprocess  # noqa
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from typing import Any
from uuid import uuid4

import httpx
from httpx import AsyncClient, AsyncHTTPTransport, Response
from loguru import logger
from pydub import AudioSegment
from speech_recognition import (
    AudioFile,
    Recognizer,
    UnknownValueError as SpeechRecognizerError,
)

from constants import (
    AUDIO_SEGMENT_DURATION,
    CHAT_GPT_BASE_URI,
    INVALID_GPT_MODEL_MESSAGE,
)
from settings.config import settings


def timed_cache(**timedelta_kwargs: Any) -> Any:
    def _wrapper(func: Any) -> Any:
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.utcnow() + update_delta
        # Apply @lru_cache to f with no cache size limit
        cached_func = lru_cache(None)(func)

        @wraps(func)
        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            nonlocal next_update
            now = datetime.utcnow()
            if now >= next_update:
                cached_func.cache_clear()
                next_update = now + update_delta
            return cached_func(*args, **kwargs)

        return _wrapped

    return _wrapper


class SpeechToTextService:
    def __init__(self, filename: str) -> None:
        self.executor = ThreadPoolExecutor()

        self.filename = filename
        self.recognizer = Recognizer()
        self.recognizer.energy_threshold = 50
        self.text_parts: dict[int, str] = {}
        self.text_recognised = False

    def get_text_from_audio(self) -> None:
        self.executor.submit(self.worker)

    def worker(self) -> Any:
        self._convert_file_to_wav()
        self._convert_audio_to_text()

    def _convert_audio_to_text(self) -> None:
        wav_filename = f"{self.filename}.wav"

        speech = AudioSegment.from_wav(wav_filename)
        speech_duration = len(speech)
        pieces = speech_duration // AUDIO_SEGMENT_DURATION + 1
        ending = speech_duration % AUDIO_SEGMENT_DURATION
        for i in range(pieces):
            if i == 0 and pieces == 1:
                sound_segment = speech[0:ending]
            elif i == 0:
                sound_segment = speech[0 : (i + 1) * AUDIO_SEGMENT_DURATION]
            elif i == (pieces - 1):
                sound_segment = speech[i * AUDIO_SEGMENT_DURATION - 250 : i * AUDIO_SEGMENT_DURATION + ending]
            else:
                sound_segment = speech[i * AUDIO_SEGMENT_DURATION - 250 : (i + 1) * AUDIO_SEGMENT_DURATION]
            self.text_parts[i] = self._recognize_by_google(wav_filename, sound_segment)

        self.text_recognised = True

        # clean temp voice message main files
        try:
            os.remove(wav_filename)
            os.remove(self.filename)
        except FileNotFoundError as error:
            logger.error("error temps files not deleted", error=error, filenames=[self.filename, self.filename])

    def _convert_file_to_wav(self) -> None:
        new_filename = self.filename + ".wav"
        cmd = ["ffmpeg", "-loglevel", "quiet", "-i", self.filename, "-vn", new_filename]
        try:
            subprocess.run(args=cmd)  # noqa: S603
            logger.info("file has been converted to wav", filename=new_filename)
        except Exception as error:
            logger.error("cant convert voice", error=error, filename=self.filename)

    def _recognize_by_google(self, filename: str, sound_segment: AudioSegment) -> str:
        tmp_filename = f"{filename}_tmp_part"
        sound_segment.export(tmp_filename, format="wav")
        with AudioFile(tmp_filename) as source:
            audio_text = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio_text, language="ru-RU")
                os.remove(tmp_filename)
                return text
            except SpeechRecognizerError as error:
                os.remove(tmp_filename)
                logger.error("error recognizing text with google", error=error)
                raise error


class ChatGptService:
    def __init__(self, chat_gpt_model: str) -> None:
        self.chat_gpt_model = chat_gpt_model

    async def request_to_chatgpt(self, question: str | None) -> str:
        question = question or "Привет!"
        chat_gpt_request = self.build_request_data(question)
        try:
            response = await self.do_request(chat_gpt_request)
            status = response.status_code
            if response.text == INVALID_GPT_MODEL_MESSAGE:
                message = f"{INVALID_GPT_MODEL_MESSAGE}: {settings.GPT_MODEL}"
                logger.info(message, data=chat_gpt_request)
                return message
            if status != httpx.codes.OK:
                logger.info(f"got response status: {status} from chat api", data=chat_gpt_request)
                return "Что-то пошло не так, попробуйте еще раз или обратитесь к администратору"
            return response.text
        except Exception as error:
            logger.error("error get data from chat api", error=error)
        return "Вообще всё сломалось :("

    @staticmethod
    async def do_request(data: dict[str, Any]) -> Response:
        transport = AsyncHTTPTransport(retries=3)
        async with AsyncClient(base_url=settings.GPT_BASE_HOST, transport=transport, timeout=50) as client:
            return await client.post(CHAT_GPT_BASE_URI, json=data, timeout=50)

    def build_request_data(self, question: str) -> dict[str, Any]:
        return {
            "conversation_id": str(uuid4()),
            "action": "_ask",
            "model": self.chat_gpt_model,
            "jailbreak": "default",
            "meta": {
                "id": random.randint(10**18, 10**19 - 1),  # noqa: S311
                "content": {
                    "conversation": [],
                    "internet_access": False,
                    "content_type": "text",
                    "parts": [{"content": question, "role": "user"}],
                },
            },
        }
