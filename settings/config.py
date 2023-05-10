import os
from os import environ
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings

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
    APP_PORT: int = 8082
    STAGE: str = "dev"
    DEBUG: bool = False

    TELEGRAM_API_TOKEN: str = "123456789:AABBCCDDEEFFaabbccddeeff-1234567890"
    START_WITH_WEBHOOK: bool = False
    # webhook settings
    WEBHOOK_HOST: str = "https://mydomain.com"
    WEBHOOK_PATH: str = "/healthcheck"

    # quantity of workers for uvicorn
    WORKERS_COUNT: int = 1
    # Enable uvicorn reloading
    RELOAD: bool = False

    @property
    def bot_webhook_url(self) -> str:
        return os.path.join(self.WEBHOOK_PATH.strip('/'), self.TELEGRAM_API_TOKEN)

    class Config:
        case_sensitive = True


def get_settings() -> Settings:
    return Settings()
