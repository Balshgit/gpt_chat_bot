from enum import StrEnum

AUDIO_SEGMENT_DURATION = 120 * 1000

API_PREFIX = "/api"
CHAT_GPT_BASE_URI = "/backend_api/v2/conversation"
INVALID_GPT_REQUEST_MESSAGES = ("Invalid request model", "return unexpected http status code")


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


class ChatGptModelsEnum(StrEnum):
    gpt_3_5_turbo_stream_openai = "gpt-3.5-turbo-stream-openai"
    gpt_3_5_turbo_Aichat = "gpt-3.5-turbo-Aichat"
    gpt_4_ChatgptAi = "gpt-4-ChatgptAi"
    gpt_3_5_turbo_weWordle = "gpt-3.5-turbo-weWordle"
    gpt_3_5_turbo_acytoo = "gpt-3.5-turbo-acytoo"
    gpt_3_5_turbo_stream_DeepAi = "gpt-3.5-turbo-stream-DeepAi"
    gpt_3_5_turbo_stream_H2o = "gpt-3.5-turbo-stream-H2o"
    gpt_3_5_turbo_stream_yqcloud = "gpt-3.5-turbo-stream-yqcloud"
    gpt_OpenAssistant_stream_HuggingChat = "gpt-OpenAssistant-stream-HuggingChat"
    gpt_4_turbo_stream_you = "gpt-4-turbo-stream-you"
    gpt_3_5_turbo_AItianhu = "gpt-3.5-turbo-AItianhu"
    gpt_3_stream_binjie = "gpt-3-stream-binjie"
    gpt_3_5_turbo_stream_CodeLinkAva = "gpt-3.5-turbo-stream-CodeLinkAva"
    gpt_4_stream_ChatBase = "gpt-4-stream-ChatBase"
    gpt_3_5_turbo_stream_aivvm = "gpt-3.5-turbo-stream-aivvm"
    gpt_3_5_turbo_16k_stream_Ylokh = "gpt-3.5-turbo-16k-stream-Ylokh"
    gpt_3_5_turbo_stream_Vitalentum = "gpt-3.5-turbo-stream-Vitalentum"
    gpt_3_5_turbo_stream_GptGo = "gpt-3.5-turbo-stream-GptGo"
    gpt_3_5_turbo_stream_AItianhuSpace = "gpt-3.5-turbo-stream-AItianhuSpace"
    gpt_3_5_turbo_stream_Aibn = "gpt-3.5-turbo-stream-Aibn"
    gpt_3_5_turbo_ChatgptDuo = "gpt-3.5-turbo-ChatgptDuo"
    gpt_3_5_turbo_stream_FreeGpt = "gpt-3.5-turbo-stream-FreeGpt"
    gpt_3_5_turbo_stream_ChatForAi = "gpt-3.5-turbo-stream-ChatForAi"

    @classmethod
    def values(cls) -> set[str]:
        return set(map(str, set(ChatGptModelsEnum)))
