from functools import cache, cached_property
from os import environ
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings
from yarl import URL

from constants import API_PREFIX, CHATGPT_BASE_URI

BASE_DIR = Path(__file__).parent.parent
SHARED_DIR = BASE_DIR.resolve().joinpath("shared")
SHARED_DIR.mkdir(exist_ok=True)

DIR_LOGS = SHARED_DIR.joinpath("logs")
DIR_LOGS.mkdir(exist_ok=True)

env_path = f"{BASE_DIR}/settings/.env"

if environ.get("STAGE") == "runtests":
    env_path = f"{BASE_DIR}/settings/.env.runtests"

load_dotenv(env_path, override=True)


class SentrySettings(BaseSettings):
    ENABLE_SENTRY: bool = False
    SENTRY_DSN: str | None = None
    DEPLOY_ENVIRONMENT: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.95

    @model_validator(mode="after")
    def validate_sentry_enabled(self) -> "SentrySettings":
        if self.ENABLE_SENTRY and not self.SENTRY_DSN:
            raise RuntimeError("sentry dsn must be set")
        return self


class LoggingSettings(BaseSettings):
    ENABLE_JSON_LOGS: bool = True
    ENABLE_SENTRY_LOGS: bool = False

    ENABLE_GRAYLOG: bool = False
    GRAYLOG_HOST: str | None = None
    GRAYLOG_PORT: int | None = None

    LOG_TO_FILE: str | None = None

    @model_validator(mode="after")
    def validate_graylog_enabled(self) -> "LoggingSettings":
        if self.ENABLE_GRAYLOG and not all([self.GRAYLOG_HOST, self.GRAYLOG_PORT]):
            raise RuntimeError("graylog host and port must be set")
        return self


class AppSettings(SentrySettings, LoggingSettings, BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "chat gpt bot"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    STAGE: str = "dev"
    DEBUG: bool = False
    # quantity of workers for uvicorn
    WORKERS_COUNT: int = 1
    # Enable uvicorn reloading
    RELOAD: bool = False

    SUPERUSER: str | None = None
    SUPERUSER_PASSWORD: SecretStr | None = None
    SALT: SecretStr | None = None

    # telegram settings
    TELEGRAM_API_TOKEN: str = "123456789:AABBCCDDEEFFaabbccddeeff-1234567890"
    START_WITH_WEBHOOK: bool = False

    # domain settings
    DOMAIN: str = "https://localhost"
    URL_PREFIX: str = ""
    CHAT_PREFIX: str = ""

    DB_NAME: str = "chatgpt.db"
    DB_ECHO: bool = False

    # ==== gpt settings ====
    GPT_BASE_HOST: str = "http://chathpt_chat_service:8858"

    @model_validator(mode="before")  # type: ignore[arg-type]
    def validate_boolean_fields(self) -> Any:
        values_dict: dict[str, Any] = self  # type: ignore[assignment]
        for value in (
            "ENABLE_JSON_LOGS",
            "ENABLE_SENTRY_LOGS",
            "START_WITH_WEBHOOK",
            "RELOAD",
            "DEBUG",
            "ENABLE_GRAYLOG",
            "ENABLE_SENTRY",
        ):
            setting_value: str | None = values_dict.get(value)
            if setting_value and setting_value.lower() == "false":
                values_dict[value] = False
        return values_dict

    @cached_property
    def api_prefix(self) -> str:
        if self.URL_PREFIX:
            return "/" + "/".join([self.URL_PREFIX.strip("/"), API_PREFIX.strip("/")])
        return API_PREFIX

    @cached_property
    def chat_prefix(self) -> str:
        return self.URL_PREFIX + self.CHAT_PREFIX

    @cached_property
    def chatgpt_backend_url(self) -> str:
        return self.chat_prefix + CHATGPT_BASE_URI

    @cached_property
    def token_part(self) -> str:
        return self.TELEGRAM_API_TOKEN[15:30]

    @cached_property
    def bot_webhook_url(self) -> str:
        return "/".join([self.api_prefix, self.token_part])

    @cached_property
    def db_file(self) -> Path:
        return SHARED_DIR / self.DB_NAME

    @cached_property
    def async_db_url(self) -> URL:
        return URL.build(
            scheme="sqlite+aiosqlite",
            path=f"///{self.db_file}",
        )

    @cached_property
    def sync_db_url(self) -> URL:
        return URL.build(
            scheme="sqlite",
            path=f"///{self.db_file}",
        )

    class Config:
        case_sensitive = True


@cache
def get_settings() -> AppSettings:
    return AppSettings()


settings = get_settings()
