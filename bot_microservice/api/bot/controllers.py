from fastapi import APIRouter, Body, Depends, Path
from starlette import status
from starlette.responses import JSONResponse, Response
from telegram import Update

from api.bot.serializers import (
    ChatGptModelSerializer,
    ChatGptModelsPrioritySerializer,
    GETChatGptModelsSerializer,
    LightChatGptModel,
)
from api.deps import get_bot_queue, get_chatgpt_service, get_update_from_request
from core.bot.app import BotQueue
from core.bot.services import ChatGptService
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


@router.get(
    "/models",
    name="bot:models_list",
    response_class=JSONResponse,
    response_model=list[ChatGptModelSerializer],
    status_code=status.HTTP_200_OK,
    summary="list of models",
)
async def models_list(
    chatgpt_service: ChatGptService = Depends(get_chatgpt_service),
) -> JSONResponse:
    """Получить список всех моделей"""
    models = await chatgpt_service.get_chatgpt_models()
    return JSONResponse(
        content=GETChatGptModelsSerializer(data=models).model_dump(), status_code=status.HTTP_200_OK  # type: ignore
    )


@router.post(
    "/models/{model_id}/priority",
    name="bot:change_model_priority",
    response_class=Response,
    status_code=status.HTTP_202_ACCEPTED,
    summary="change gpt model priority",
)
async def change_model_priority(
    model_id: int = Path(..., gt=0, description="Id модели для обновления приореитета"),
    chatgpt_service: ChatGptService = Depends(get_chatgpt_service),
    gpt_model: ChatGptModelsPrioritySerializer = Body(...),
) -> None:
    """Изменить приоритет модели в выдаче"""
    await chatgpt_service.change_chatgpt_model_priority(model_id=model_id, priority=gpt_model.priority)


@router.post(
    "/models",
    name="bot:add_new_model",
    response_model=ChatGptModelSerializer,
    status_code=status.HTTP_201_CREATED,
    summary="add new model",
)
async def add_new_model(
    chatgpt_service: ChatGptService = Depends(get_chatgpt_service),
    gpt_model: LightChatGptModel = Body(...),
) -> JSONResponse:
    """Добавить новую модель"""
    model = await chatgpt_service.add_chatgpt_model(gpt_model=gpt_model.model, priority=gpt_model.priority)

    return JSONResponse(content=model, status_code=status.HTTP_201_CREATED)


@router.delete(
    "/models/{model_id}",
    name="bot:delete_gpt_model",
    response_class=Response,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="delete gpt model",
)
async def delete_model(
    model_id: int = Path(..., gt=0, description="Id модели для удаления"),
    chatgpt_service: ChatGptService = Depends(get_chatgpt_service),
) -> None:
    """Удалить gpt модель"""
    await chatgpt_service.delete_chatgpt_model(model_id=model_id)
