import asyncio
from functools import cached_property

import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from api.exceptions import internal_server_error_handler
from core.bot.app import BotApplication, BotQueue
from core.bot.handlers import bot_event_handlers
from core.lifetime import shutdown, startup
from infra.admin import create_admin
from infra.database.db_adapter import Database
from infra.logging_conf import configure_logging
from routers import api_router
from settings.config import AppSettings, get_settings


class Application:
    def __init__(self, settings: AppSettings, bot_app: BotApplication) -> None:
        self.app = FastAPI(
            title="Chat gpt bot",
            description="Bot for proxy to chat gpt in telegram",
            version="0.0.3",
            docs_url="/" + "/".join([settings.api_prefix.strip("/"), "docs"]),
            redoc_url="/" + "/".join([settings.api_prefix.strip("/"), "redocs"]),
            openapi_url="/" + "/".join([settings.api_prefix.strip("/"), "openapi.json"]),
            debug=settings.DEBUG,
            default_response_class=UJSONResponse,
            exception_handlers={
                Exception: internal_server_error_handler,
            },
        )
        self.bot_app = bot_app
        self.db = Database(settings)
        self._bot_queue = BotQueue(bot_app=self.bot_app)
        self.app.state.settings = settings
        self.app.state.queue = self._bot_queue
        self.app.state.bot_app = self.bot_app

        self.app.on_event("startup")(startup(self.app, self.db))
        self.app.on_event("shutdown")(shutdown(self.app))

        self.app.include_router(api_router)
        self.configure_bot_hooks()
        configure_logging(
            level=settings.LOG_LEVEL,
            enable_json_logs=settings.ENABLE_JSON_LOGS,
            enable_sentry_logs=settings.ENABLE_SENTRY_LOGS,
            log_to_file=settings.LOG_TO_FILE,
        )

        if settings.ENABLE_SENTRY:
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.DEPLOY_ENVIRONMENT,
                traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
                send_client_reports=False,
            )

    @cached_property
    def fastapi_app(self) -> FastAPI:
        return self.app

    @cached_property
    def bot_queue(self) -> BotQueue:
        return self._bot_queue

    def configure_bot_hooks(self) -> None:
        if self.bot_app.start_with_webhook:
            self.app.add_event_handler("startup", self._bot_start_up)
        else:
            self.app.add_event_handler("startup", self.bot_app.polling)

        self.app.add_event_handler("shutdown", self._bot_shutdown)

    async def _bot_start_up(self) -> None:
        await self.bot_app.set_webhook()
        loop = asyncio.get_event_loop()
        loop.create_task(self.app.state.queue.get_updates_from_queue())

    async def _bot_shutdown(self) -> None:
        await self.bot_app.shutdown()


def create_app(settings: AppSettings | None = None) -> FastAPI:
    settings = settings or get_settings()
    bot_app = BotApplication(settings=settings, handlers=bot_event_handlers.handlers)

    application = Application(settings=settings, bot_app=bot_app)
    create_admin(application)

    return application.fastapi_app


def main() -> None:
    import uvicorn

    app = create_app()  # noqa: NEW100

    """Entrypoint of the application."""
    uvicorn.run(
        "main:create_app",
        workers=app.state.settings.WORKERS_COUNT,
        host=app.state.settings.APP_HOST,
        port=app.state.settings.APP_PORT,
        reload=app.state.settings.RELOAD,
        factory=True,
    )


if __name__ == "__main__":
    main()
