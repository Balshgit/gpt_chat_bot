import asyncio
import sys
from functools import cached_property

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from loguru import logger

from app.core.bot import BotApplication, BotQueue
from app.routers import api_router
from settings.config import AppSettings, get_settings

logger.remove()
logger.add(
    sink=sys.stdout,
    colorize=True,
    level="DEBUG",
    format="<cyan>{time:DD.MM.YYYY HH:mm:ss}</cyan> | <level>{level}</level> | <magenta>{message}</magenta>",
)


class Application:
    def __init__(self, settings: AppSettings, bot_app: BotApplication) -> None:
        self.app = FastAPI(
            title="Chat gpt bot",
            description="Bot for proxy to chat gpt in telegram",
            version="0.0.3",
            docs_url="/" + "/".join([settings.api_prefix.strip("/"), "docs"]),
            redoc_url="/" + "/".join([settings.api_prefix.strip("/"), "redocs"]),
            openapi_url="/" + "/".join([settings.api_prefix.strip("/"), "openapi.json"]),
            default_response_class=UJSONResponse,
        )
        self.app.state.settings = settings
        self.app.state.queue = BotQueue(bot_app=bot_app)
        self.bot_app = bot_app

        self.app.include_router(api_router)
        self.configure_hooks()

    @cached_property
    def fastapi_app(self) -> FastAPI:
        return self.app

    def configure_hooks(self) -> None:
        if self.bot_app.start_with_webhook:
            self.app.add_event_handler("startup", self._on_start_up)
        else:
            self.app.add_event_handler("startup", self.bot_app.polling)

        self.app.add_event_handler("shutdown", self._on_shutdown)

    async def _on_start_up(self) -> None:
        await self.bot_app.set_webhook()
        loop = asyncio.get_event_loop()
        loop.create_task(self.app.state.queue.get_updates_from_queue())

    async def _on_shutdown(self) -> None:
        await asyncio.gather(self.bot_app.delete_webhook(), self.bot_app.shutdown())


def create_app(settings: AppSettings | None = None) -> FastAPI:
    settings = settings or get_settings()
    bot_app = BotApplication(settings=settings)

    return Application(settings=settings, bot_app=bot_app).fastapi_app


def main() -> None:
    import uvicorn

    app = create_app()  # noqa: NEW100

    """Entrypoint of the application."""
    uvicorn.run(
        "app.main:create_app",
        workers=app.state.settings.WORKERS_COUNT,
        host=app.state.settings.APP_HOST,
        port=app.state.settings.APP_PORT,
        reload=app.state.settings.RELOAD,
        factory=True,
    )


if __name__ == "__main__":
    main()
