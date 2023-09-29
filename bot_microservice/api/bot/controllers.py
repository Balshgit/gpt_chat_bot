from fastapi import APIRouter, Request
from starlette import status
from starlette.responses import Response

from constants import INVALID_GPT_MODEL_MESSAGE
from core.utils import ChatGptService
from settings.config import settings

router = APIRouter()


@router.post(
    f"/{settings.TELEGRAM_API_TOKEN}",
    name="bot:process_bot_updates",
    response_class=Response,
    status_code=status.HTTP_202_ACCEPTED,
    summary="process bot updates",
    include_in_schema=False,
)
async def process_bot_updates(request: Request) -> None:
    await request.app.state.queue.put_updates_on_queue(request)


@router.get(
    "/bot-healthcheck",
    name="bot:gpt_healthcheck",
    response_class=Response,
    summary="bot healthcheck",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Request to chat gpt not success"},
        status.HTTP_200_OK: {"description": "Successful Response"},
    },
)
async def gpt_healthcheck(response: Response) -> Response:
    chat_gpt_service = ChatGptService(chat_gpt_model=settings.GPT_MODEL)
    data = chat_gpt_service.build_request_data('Привет!')
    try:
        gpt_response = await chat_gpt_service.do_request(data)
        if gpt_response.text == INVALID_GPT_MODEL_MESSAGE or response.status_code != status.HTTP_200_OK:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    except Exception:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return Response(status_code=response.status_code, content=None)
