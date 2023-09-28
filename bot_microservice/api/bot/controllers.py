from fastapi import APIRouter, Request
from starlette import status
from starlette.responses import Response

from settings.config import settings

router = APIRouter()


@router.post(
    f"/{settings.TELEGRAM_API_TOKEN}",
    name="system:process_bot_updates",
    response_class=Response,
    status_code=status.HTTP_202_ACCEPTED,
    summary="process bot updates",
    include_in_schema=False,
)
async def process_bot_updates(request: Request) -> None:
    await request.app.state.queue.put_updates_on_queue(request)
