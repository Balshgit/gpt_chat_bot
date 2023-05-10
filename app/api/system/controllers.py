from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse
from starlette import status

from settings.config import get_settings

router = APIRouter()


@router.get(
    "/healthcheck",
    name="system:healthcheck",
    status_code=status.HTTP_200_OK,
    summary="Healthcheck service",
)
async def healthcheck() -> ORJSONResponse:
    return ORJSONResponse(content=None, status_code=status.HTTP_200_OK)


@router.post(
    f"/{get_settings().bot_webhook_url}",
    name="system:process_bot_updates",
    status_code=status.HTTP_202_ACCEPTED,
    summary="process bot updates",
)
async def process_bot_updates(request: Request) -> ORJSONResponse:
    await request.app.state.queue.put_updates_on_queue(request)
    data = await request.app.state.queue.get_updates_from_queue()
    print(data)
    return ORJSONResponse(content=None, status_code=status.HTTP_202_ACCEPTED)
