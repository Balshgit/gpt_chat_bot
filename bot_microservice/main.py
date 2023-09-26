import asyncio
from functools import cached_property

import sentry_sdk
from constants import LogLevelEnum
from core.bot import BotApplication, BotQueue
from core.handlers import bot_event_handlers
from core.logging import configure_logging
from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from routers import api_router
from settings.config import AppSettings, get_settings


class Application:
    def __init__(self, settings: AppSettings, bot_app: BotApplication) -> None:
        print('Hello World')
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
        configure_logging(level=LogLevelEnum.INFO, enable_json_logs=True, enable_sentry_logs=True)

        if settings.SENTRY_DSN is not None:
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,  # type: ignore[arg-type]
                environment=settings.DEPLOY_ENVIRONMENT,
                traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
                send_client_reports=False,
            )

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
    bot_app = BotApplication(settings=settings, handlers=bot_event_handlers.handlers)

    return Application(settings=settings, bot_app=bot_app).fastapi_app


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
