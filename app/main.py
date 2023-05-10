import sys
from functools import cached_property

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from loguru import logger

from app.core.bot import Bot, BotQueue
from app.routers import api_router
from settings.config import Settings, get_settings

logger.remove()
logger.add(
    sink=sys.stdout,
    colorize=True,
    level='DEBUG',
    format="<cyan>{time:DD.MM.YYYY HH:mm:ss}</cyan> | <level>{level}</level> | <magenta>{message}</magenta>",
)


class Application:
    def __init__(self, settings: Settings) -> None:
        self.app = FastAPI(
            title='Health check bot',
            description='Bot which check all services are working',
            version='0.0.1',
            docs_url=f'{settings.WEBHOOK_PATH}/docs',
            redoc_url=f'{settings.WEBHOOK_PATH}/redocs',
            openapi_url=f'{settings.WEBHOOK_PATH}/api/openapi.json',
            default_response_class=UJSONResponse,
        )
        self.app.state.settings = settings
        self.settings = settings
        self.app.include_router(api_router)
        self.configure_hooks()

    @property
    def fastapi_app(self) -> FastAPI:
        return self.app

    @cached_property
    def bot(self) -> Bot:
        return Bot(self.settings)

    def set_bot_queue(self) -> None:
        self.app.state.queue = BotQueue(bot=self.bot)

    def configure_hooks(self) -> None:
        self.app.add_event_handler("startup", self.bot.set_webhook)
        # self.app.add_event_handler("startup", self.bot.polling)  # noqa: E800
        self.app.add_event_handler("startup", self.set_bot_queue)

        self.app.add_event_handler("shutdown", self.bot.delete_webhook)
        self.app.add_event_handler("shutdown", self.bot.shutdown)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    return Application(settings=settings).fastapi_app


def main() -> None:
    import uvicorn

    app = create_app()

    """Entrypoint of the application."""
    uvicorn.run(
        "app.main:create_app",
        workers=app.state.settings.WORKERS_COUNT,
        host=app.state.settings.APP_HOST,
        port=app.state.settings.APP_PORT,
        # reload=app.state.settings.RELOAD,  # noqa: E800 remove reload for debug
        factory=True,
    )


if __name__ == '__main__':
    main()
