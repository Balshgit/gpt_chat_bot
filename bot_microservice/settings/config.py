from functools import cached_property
from os import environ
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings

from constants import API_PREFIX

BASE_DIR = Path(__file__).parent.parent
SHARED_DIR = BASE_DIR.resolve().joinpath("shared")
SHARED_DIR.mkdir(exist_ok=True)

SHARED_DIR.joinpath("logs").mkdir(exist_ok=True)
DIR_LOGS = SHARED_DIR.joinpath("logs")

env_path = f"{BASE_DIR}/settings/.env"

if environ.get("STAGE") == "runtests":
    if "LOCALTEST" in environ:
        env_path = f"{BASE_DIR}/settings/.env.local.runtests"
    else:
        env_path = f"{BASE_DIR}/settings/.env.ci.runtests"

load_dotenv(env_path, override=True)


class SentrySettings(BaseSettings):
    SENTRY_DSN: str | None = None
    DEPLOY_ENVIRONMENT: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.95


class AppSettings(SentrySettings, BaseSettings):
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

    TELEGRAM_API_TOKEN: str = "123456789:AABBCCDDEEFFaabbccddeeff-1234567890"
    # webhook settings
    START_WITH_WEBHOOK: bool = False
    DOMAIN: str = "https://localhost"
    URL_PREFIX: str = ""

    # ==== gpt settings ====
    GPT_MODEL: str = "gpt-3.5-turbo-stream-DeepAi"
    GPT_BASE_HOST: str = "http://chat_service:8858"

    ENABLE_JSON_LOGS: bool = True
    ENABLE_SENTRY_LOGS: bool = False
    GRAYLOG_HOST: str | None = None
    GRAYLOG_PORT: int | None = None
    LOG_TO_FILE: str | None = None

    @model_validator(mode="before")  # type: ignore[arg-type]
    def validate_boolean_fields(self) -> Any:
        for value in (
            "ENABLE_JSON_LOGS",
            "ENABLE_SENTRY_LOGS",
            "START_WITH_WEBHOOK",
            "RELOAD",
            "DEBUG",
        ):
            setting_value: str = self.get(value)  # type: ignore[attr-defined]
            if setting_value and setting_value.lower() == "false":
                self[value] = False  # type: ignore[index]
        return self

    @cached_property
    def api_prefix(self) -> str:
        if self.URL_PREFIX:
            return "/" + "/".join([self.URL_PREFIX.strip("/"), API_PREFIX.strip("/")])
        return API_PREFIX

    @cached_property
    def bot_webhook_url(self) -> str:
        return "/".join([self.api_prefix, self.TELEGRAM_API_TOKEN])

    class Config:
        case_sensitive = True


def get_settings() -> AppSettings:
    return AppSettings()


settings = get_settings()
