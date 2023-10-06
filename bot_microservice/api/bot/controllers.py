from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response
from telegram import Update

from api.deps import get_bot_queue, get_update_from_request
from core.bot.app import BotQueue
from settings.config import settings

router = APIRouter()


@router.post(
    f"/{settings.token_part}",
    name="bot:process_bot_updates",
    response_class=Response,
    status_code=status.HTTP_202_ACCEPTED,
    summary="process bot updates",
    include_in_schema=False,
)
async def process_bot_updates(
    tg_update: Update = Depends(get_update_from_request),
    queue: BotQueue = Depends(get_bot_queue),
) -> None:
    await queue.put_updates_on_queue(tg_update)
