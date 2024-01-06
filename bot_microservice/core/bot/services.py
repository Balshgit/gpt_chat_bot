import os
import subprocess  # noqa: S404
import tempfile
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Sequence

from httpx import Response
from loguru import logger
from pydub import AudioSegment
from speech_recognition import (
    AudioFile,
    Recognizer,
    UnknownValueError as SpeechRecognizerError,
)

from constants import AUDIO_SEGMENT_DURATION
from core.auth.repository import UserRepository
from core.auth.services import UserService
from core.bot.models.chatgpt import ChatGptModels
from core.bot.repository import ChatGPTRepository
from infra.database.db_adapter import Database
from settings.config import settings


class SpeechToTextService:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.executor = ThreadPoolExecutor()
        self.recognizer = Recognizer()
        self.recognizer.energy_threshold = 50
        self.text_parts: dict[int, str] = {}
        self.text_recognised = False

    def get_text_from_audio(self) -> None:
        self.executor.submit(self._worker)

    def _worker(self) -> Any:
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
            self.text_parts[i] = self._recognize_by_google(sound_segment)

        self.text_recognised = True

        # clean temp voice message main files
        try:
            os.remove(wav_filename)
            os.remove(self.filename)
        except FileNotFoundError as error:
            logger.error("error temps files not deleted", error=error, filenames=[self.filename, wav_filename])

    def _convert_file_to_wav(self) -> None:
        new_filename = self.filename + ".wav"
        cmd = ["ffmpeg", "-loglevel", "quiet", "-i", self.filename, "-vn", new_filename]
        try:
            subprocess.run(args=cmd, check=True)  # noqa: S603
            logger.info("file has been converted to wav", filename=new_filename)
        except Exception as error:
            logger.error("cant convert voice", error=error, filename=self.filename)

    def _recognize_by_google(self, sound_segment: AudioSegment) -> str:
        with tempfile.NamedTemporaryFile(delete=True) as tmpfile:
            tmpfile.write(sound_segment.raw_data)
            sound_segment.export(tmpfile, format="wav")
            with AudioFile(tmpfile) as source:
                audio_text = self.recognizer.listen(source)
                try:
                    return self.recognizer.recognize_sphinx(audio_text, language="ru-RU")
                except SpeechRecognizerError as error:
                    logger.error("error recognizing text with google", error=error)
                    raise


@dataclass
class ChatGptService:
    repository: ChatGPTRepository
    user_service: UserService

    async def get_chatgpt_models(self) -> Sequence[ChatGptModels]:
        return await self.repository.get_chatgpt_models()

    async def request_to_chatgpt(self, question: str | None) -> str:
        question = question or "Привет!"
        chatgpt_model = await self.get_current_chatgpt_model()
        return await self.repository.ask_question(question=question, chatgpt_model=chatgpt_model)

    async def request_to_chatgpt_microservice(self, question: str) -> Response:
        chatgpt_model = await self.get_current_chatgpt_model()
        return await self.repository.request_to_chatgpt_microservice(question=question, chatgpt_model=chatgpt_model)

    async def get_current_chatgpt_model(self) -> str:
        return await self.repository.get_current_chatgpt_model()

    async def change_chatgpt_model_priority(self, model_id: int, priority: int) -> None:
        return await self.repository.change_chatgpt_model_priority(model_id=model_id, priority=priority)

    async def reset_all_chatgpt_models_priority(self) -> None:
        return await self.repository.reset_all_chatgpt_models_priority()

    async def add_chatgpt_model(self, gpt_model: str, priority: int) -> dict[str, str | int]:
        return await self.repository.add_chatgpt_model(model=gpt_model, priority=priority)

    async def delete_chatgpt_model(self, model_id: int) -> None:
        return await self.repository.delete_chatgpt_model(model_id=model_id)

    @classmethod
    def build(cls) -> "ChatGptService":
        db = Database(settings=settings)
        repository = ChatGPTRepository(settings=settings, db=db)
        user_repository = UserRepository(db=db)
        user_service = UserService(repository=user_repository)
        return ChatGptService(repository=repository, user_service=user_service)
