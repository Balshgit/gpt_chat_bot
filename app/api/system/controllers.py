from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse
from starlette import status

from settings.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get(
    "/healthcheck",
    name="system:healthcheck",
    status_code=status.HTTP_200_OK,
    summary="Healthcheck service",
)
async def healthcheck() -> ORJSONResponse:
    return ORJSONResponse(content=None, status_code=status.HTTP_200_OK)


@router.post(
    f"/{settings.bot_webhook_url}",
    name="system:process_bot_updates",
    status_code=status.HTTP_202_ACCEPTED,
    summary="process bot updates",
    include_in_schema=False,
)
async def process_bot_updates(request: Request) -> ORJSONResponse:
    await request.app.state.queue.put_updates_on_queue(request)
    return ORJSONResponse(content=None, status_code=status.HTTP_202_ACCEPTED)
