from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from app.routers import api_router
from settings.config import Settings, get_settings


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

    @property
    def fastapi_app(self) -> FastAPI:
        return self.app

    def configure_hooks(self) -> None:
        self.app.add_event_handler("startup", self.connect_databases)  # type: ignore
        self.app.add_event_handler("startup", self.create_redis_cluster)  # type: ignore

        self.app.add_event_handler("shutdown", self.disconnect_databases)  # type: ignore
        self.app.add_event_handler("shutdown", self.close_redis_cluster)  # type: ignore


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
        reload=app.state.settings.RELOAD,
        factory=True,
    )


if __name__ == '__main__':
    main()
