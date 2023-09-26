from enum import StrEnum

AUDIO_SEGMENT_DURATION = 120 * 1000

API_PREFIX = "/api"
CHAT_GPT_BASE_URL = "http://chat_service:1338/backend-api/v2/conversation"


class LogLevelEnum(StrEnum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    NOTSET = ""
