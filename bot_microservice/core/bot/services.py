import os
import subprocess  # noqa
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from httpx import Response
from loguru import logger
from pydub import AudioSegment
from speech_recognition import (
    AudioFile,
    Recognizer,
    UnknownValueError as SpeechRecognizerError,
)

from constants import AUDIO_SEGMENT_DURATION
from core.bot.repository import ChatGPTRepository
from infra.database.db_adapter import Database
from settings.config import settings


class SpeechToTextService:
    def __init__(self) -> None:
        self.executor = ThreadPoolExecutor()
        self.recognizer = Recognizer()
        self.recognizer.energy_threshold = 50
        self.text_parts: dict[int, str] = {}
        self.text_recognised = False

    def get_text_from_audio(self, filename: str) -> None:
        self.executor.submit(self.worker, filename=filename)

    def worker(self, filename: str) -> Any:
        self._convert_file_to_wav(filename)
        self._convert_audio_to_text(filename)

    def _convert_audio_to_text(self, filename: str) -> None:
        wav_filename = f"{filename}.wav"

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
            os.remove(filename)
        except FileNotFoundError as error:
            logger.error("error temps files not deleted", error=error, filenames=[filename, wav_filename])

    @staticmethod
    def _convert_file_to_wav(filename: str) -> None:
        new_filename = filename + ".wav"
        cmd = ["ffmpeg", "-loglevel", "quiet", "-i", filename, "-vn", new_filename]
        try:
            subprocess.run(args=cmd)  # noqa: S603
            logger.info("file has been converted to wav", filename=new_filename)
        except Exception as error:
            logger.error("cant convert voice", error=error, filename=filename)

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


@dataclass
class ChatGptService:
    repository: ChatGPTRepository

    async def request_to_chatgpt(self, question: str | None) -> str:
        question = question or "Привет!"
        chat_gpt_model = await self.get_current_chatgpt_model()
        return await self.repository.ask_question(question=question, chat_gpt_model=chat_gpt_model)

    async def request_to_chatgpt_microservice(self, question: str) -> Response:
        chat_gpt_model = await self.get_current_chatgpt_model()
        return await self.repository.request_to_chatgpt_microservice(question=question, chat_gpt_model=chat_gpt_model)

    async def get_current_chatgpt_model(self) -> str:
        return await self.repository.get_current_chatgpt_model()

    @classmethod
    def build(cls) -> "ChatGptService":
        db = Database(settings=settings)
        repository = ChatGPTRepository(settings=settings, db=db)
        return ChatGptService(repository=repository)
