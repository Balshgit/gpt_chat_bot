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


class BotCommands(StrEnum):
    help = "help"
    bug_report = "bug_report"
    website = "website"
    developer = "developer"


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
    gpt_3_5_turbo_stream_yqcloud = "gpt-3.5-turbo-stream-yqcloud"
    gpt_4_turbo_stream_you = "gpt-4-turbo-stream-you"
    gpt_3_stream_binjie = "gpt-3-stream-binjie"
    gpt_3_5_turbo_stream_CodeLinkAva = "gpt-3.5-turbo-stream-CodeLinkAva"
    gpt_4_stream_ChatBase = "gpt-4-stream-ChatBase"
    gpt_3_5_turbo_stream_FreeGpt = "gpt-3.5-turbo-stream-FreeGpt"
    gpt_3_5_turbo_stream_Cromicle = "gpt-3.5-turbo-stream-Cromicle"
    Llama_2_70b_chat_hf_stream_DeepInfra = "Llama-2-70b-chat-hf-stream-DeepInfra"
    gpt_4_stream_aivvm = "gpt-4-stream-aivvm"
    llama2_70B = "llama2-70B"
    gpt_3_5_turbo_stream_Berlin = "gpt-3.5-turbo-stream-Berlin"
    gpt_3_5_turbo_stream_GeekGpt = "gpt-3.5-turbo-stream-GeekGpt"
    gpt_3_5_turbo_stream_gptforlove = "gpt-3.5-turbo-stream-gptforlove"
    gpt_3_5_turbo_stream_flowgpt = "gpt-3.5-turbo-stream-flowgpt"

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
            fields = {"model": model, "priority": priority}
            models.append(fields)
        return models

    @staticmethod
    def _deprecated() -> set[str]:
        return {
            "gpt-3.5-turbo-stream-GeekGpt",
            "gpt-3.5-turbo-gptChatly",
            "gpt-3.5-turbo-stream-fakeGpt",
            "gpt-3.5-turbo-stream-aura",
            "gpt-3.5-turbo-stream-geminiProChat",
        }
