from enum import StrEnum

AUDIO_SEGMENT_DURATION = 120 * 1000

API_PREFIX = "/api"
CHAT_GPT_BASE_URI = "/backend-api/v2/conversation"
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
