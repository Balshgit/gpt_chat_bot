import os
from functools import cached_property
from os import environ
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent
SHARED_DIR = BASE_DIR.resolve().joinpath('shared')
SHARED_DIR.mkdir(exist_ok=True)

SHARED_DIR.joinpath('logs').mkdir(exist_ok=True)
DIR_LOGS = SHARED_DIR.joinpath('logs')

env_path = f"{BASE_DIR}/settings/.env"

if environ.get("STAGE") == "runtests":
    if "LOCALTEST" in environ:
        env_path = f"{BASE_DIR}/settings/.env.local.runtests"
    else:
        env_path = f"{BASE_DIR}/settings/.env.ci.runtests"

load_dotenv(env_path, override=True)


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "healthcheck bot"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    STAGE: str = "dev"
    DEBUG: bool = False

    TELEGRAM_API_TOKEN: str = "123456789:AABBCCDDEEFFaabbccddeeff-1234567890"
    # webhook settings
    START_WITH_WEBHOOK: bool = False
    WEBHOOK_HOST: str = "https://mydomain.com"
    URL_PREFIX: str = ""

    # quantity of workers for uvicorn
    WORKERS_COUNT: int = 1
    # Enable uvicorn reloading
    RELOAD: bool = False

    @cached_property
    def bot_webhook_url(self) -> str:
        return "/" + self.TELEGRAM_API_TOKEN

    class Config:
        case_sensitive = True


def get_settings() -> Settings:
    return Settings()
