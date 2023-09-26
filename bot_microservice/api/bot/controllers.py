from fastapi import APIRouter, Request
from settings.config import get_settings
from starlette import status
from starlette.responses import Response

router = APIRouter()
settings = get_settings()


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
