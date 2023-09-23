from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse
from starlette import status

from settings.config import get_settings

router = APIRouter()
settings = get_settings()


@router.post(
    f"/{settings.TELEGRAM_API_TOKEN}",
    name="system:process_bot_updates",
    status_code=status.HTTP_202_ACCEPTED,
    summary="process bot updates",
    include_in_schema=False,
)
async def process_bot_updates(request: Request) -> ORJSONResponse:
    await request.app.state.queue.put_updates_on_queue(request)
    return ORJSONResponse(content=None, status_code=status.HTTP_202_ACCEPTED)
