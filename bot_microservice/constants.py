from datetime import timezone
from enum import StrEnum, unique
from typing import Any

from dateutil import tz

AUDIO_SEGMENT_DURATION = 120 * 1000

API_PREFIX = "/api"
CHATGPT_BASE_URI = "/backend-api/v2/conversation"
INVALID_GPT_REQUEST_MESSAGES = ("Invalid request model", "return unexpected http status code")

MOSCOW_TZ = tz.gettz("Europe/Moscow")
UTC_TZ = timezone.utc


class BotStagesEnum(StrEnum):
    about_me = "about_me"
    website = "website"
    about_bot = "about_bot"
    github = "github"
    help = "help"


class BotEntryPoints(StrEnum):
    start_routes = "start_routes"
    end = "end"


class LogLevelEnum(StrEnum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    NOTSET = ""


@unique
class ChatGptModelsEnum(StrEnum):
    gpt_3_5_turbo_stream_openai = "gpt-3.5-turbo-stream-openai"
    gpt_4_ChatgptAi = "gpt-4-ChatgptAi"
    gpt_3_5_turbo_weWordle = "gpt-3.5-turbo-weWordle"
    gpt_3_5_turbo_stream_DeepAi = "gpt-3.5-turbo-stream-DeepAi"
    gpt_3_5_turbo_stream_yqcloud = "gpt-3.5-turbo-stream-yqcloud"
    gpt_OpenAssistant_stream_HuggingChat = "gpt-OpenAssistant-stream-HuggingChat"
    gpt_4_turbo_stream_you = "gpt-4-turbo-stream-you"
    gpt_3_stream_binjie = "gpt-3-stream-binjie"
    gpt_3_5_turbo_stream_CodeLinkAva = "gpt-3.5-turbo-stream-CodeLinkAva"
    gpt_4_stream_ChatBase = "gpt-4-stream-ChatBase"
    gpt_3_5_turbo_stream_GptGo = "gpt-3.5-turbo-stream-GptGo"
    gpt_3_5_turbo_stream_FreeGpt = "gpt-3.5-turbo-stream-FreeGpt"
    gpt_3_5_turbo_stream_Cromicle = "gpt-3.5-turbo-stream-Cromicle"
    gpt_3_5_turbo_stream_gptalk = "gpt-3.5-turbo-stream-gptalk"
    gpt_3_5_turbo_stream_ChatgptDemo = "gpt-3.5-turbo-stream-ChatgptDemo"
    gpt_3_5_turbo_stream_ChatAnywhere = "gpt-3.5-turbo-stream-ChatAnywhere"
    llama2 = "llama2"
    gpt_3_5_turbo_stream_Berlin = "gpt-3.5-turbo-stream-Berlin"
    gpt_4_ChatGpt4Online = "gpt-4-ChatGpt4Online"
    gpt_3_5_turbo_stream_chatGptAi = "gpt-3.5-turbo-stream-chatGptAi"
    gpt_3_5_turbo_stream_FakeGpt = "gpt-3.5-turbo-stream-FakeGpt"
    gpt_3_5_turbo_stream_GeekGpt = "gpt-3.5-turbo-stream-GeekGpt"
    gpt_3_5_turbo_stream_gptforlove = "gpt-3.5-turbo-stream-gptforlove"
    gpt_3_5_turbo_stream_Vercel = "gpt-3.5-turbo-stream-Vercel"
    gpt_3_5_turbo_stream_aivvm = "gpt-3.5-turbo-stream-aivvm"
    gpt_3_5_turbo_stream_ChatForAi = "gpt-3.5-turbo-stream-ChatForAi"

    @classmethod
    def values(cls) -> set[str]:
        return set(map(str, filter(lambda m: m not in ChatGptModelsEnum._deprecated(), cls)))

    @staticmethod
    def base_models_priority() -> list[dict[str, Any]]:
        models = []
        for model in ChatGptModelsEnum.values():
            priority = 0
            match model:
                case "gpt-3-stream-binjie":
                    priority = 3
                case "gpt-3.5-turbo-stream-yqcloud":
                    priority = 3
                case "gpt-3.5-turbo-stream-GeekGpt":
                    priority = 2
                case "gpt-3.5-turbo-stream-FakeGpt":
                    priority = 2
                case "gpt-3.5-turbo-stream-gptalk":
                    priority = 1
                case "llama2":
                    priority = 1
            fields = {"model": model, "priority": priority}
            models.append(fields)
        return models

    @staticmethod
    def _deprecated() -> set[str]:
        return {
            "gpt-3.5-turbo-stream-gptforlove",
            "gpt-3.5-turbo-stream-Vercel",
        }
