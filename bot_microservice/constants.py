from enum import IntEnum, StrEnum, auto

AUDIO_SEGMENT_DURATION = 120 * 1000

API_PREFIX = "/api"
CHAT_GPT_BASE_URL = "http://chat_service:8858/backend-api/v2/conversation"


class BotStagesEnum(IntEnum):
    about_me = auto()
    website = auto()
    help = auto()
    about_bot = auto()


class BotEntryPoints(IntEnum):
    start_routes = auto()
    end = auto()


class LogLevelEnum(StrEnum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    NOTSET = ""
