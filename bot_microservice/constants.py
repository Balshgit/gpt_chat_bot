from datetime import timezone
from enum import StrEnum, unique

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
    help = "help"
    about_bot = "about_bot"


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
    gpt_3_5_turbo_16k_stream_Ylokh = "gpt-3.5-turbo-16k-stream-Ylokh"
    gpt_3_5_turbo_stream_Vitalentum = "gpt-3.5-turbo-stream-Vitalentum"
    gpt_3_5_turbo_stream_GptGo = "gpt-3.5-turbo-stream-GptGo"
    gpt_3_5_turbo_stream_Aibn = "gpt-3.5-turbo-stream-Aibn"
    gpt_3_5_turbo_stream_FreeGpt = "gpt-3.5-turbo-stream-FreeGpt"
    gpt_3_5_turbo_stream_Cromicle = "gpt-3.5-turbo-stream-Cromicle"
    gpt_4_stream_Chatgpt4Online = "gpt-4-stream-Chatgpt4Online"
    gpt_3_5_turbo_stream_gptalk = "gpt-3.5-turbo-stream-gptalk"
    llama2 = "llama2"
    gpt_3_5_turbo_stream_ChatgptDemo = "gpt-3.5-turbo-stream-ChatgptDemo"
    gpt_3_5_turbo_stream_gptforlove = "gpt-3.5-turbo-stream-gptforlove"

    @classmethod
    def values(cls) -> set[str]:
        return set(map(str, filter(lambda m: m not in ChatGptModelsEnum._deprecated(), cls)))

    @staticmethod
    def _deprecated() -> set[str]:
        return {
            "gpt-3.5-turbo-stream-gptforlove",
            "gpt-3.5-turbo-stream-aivvm",
        }
