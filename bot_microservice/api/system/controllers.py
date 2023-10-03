from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.responses import Response

from constants import INVALID_GPT_REQUEST_MESSAGES
from core.utils import ChatGptService
from settings.config import settings

router = APIRouter()


@router.get(
    "/healthcheck",
    name="system:healthcheck",
    status_code=status.HTTP_200_OK,
    summary="Healthcheck service",
)
async def healthcheck() -> ORJSONResponse:
    return ORJSONResponse(content=None, status_code=status.HTTP_200_OK)


@router.get(
    "/bot-healthcheck",
    name="system:gpt_healthcheck",
    response_class=Response,
    summary="Проверяет доступность моделей и если они недоступны, то возвращает код ответа 500",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Request to chat gpt not success"},
        status.HTTP_200_OK: {"description": "Successful Response"},
    },
)
async def gpt_healthcheck(response: Response) -> Response:
    chatgpt_service = ChatGptService(chat_gpt_model=settings.GPT_MODEL)
    data = chatgpt_service.build_request_data("Привет!")
    response.status_code = status.HTTP_200_OK
    try:
        chatgpt_response = await chatgpt_service.do_request(data)
        if chatgpt_response.status_code != status.HTTP_200_OK:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        for message in INVALID_GPT_REQUEST_MESSAGES:
            if message in chatgpt_response.text:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    except Exception:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return Response(status_code=response.status_code, content=None)
