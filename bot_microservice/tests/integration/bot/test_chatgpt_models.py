import pytest
from sqlalchemy.orm import Session

from constants import ChatGptModelsEnum
from core.bot.models.chatgpt import ChatGptModels
from core.bot.services import ChatGptService
from tests.integration.factories.bot import ChatGptModelFactory

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.enable_socket,
]


async def test_models_creation(dbsession: Session) -> None:
    models = dbsession.query(ChatGptModels).all()

    assert len(models) == 0

    chatgpt_service = ChatGptService.build()

    await chatgpt_service.update_chatgpt_models()

    models = dbsession.query(ChatGptModels).all()

    model_priorities = {model.model: model.priority for model in models}

    assert len(models) == len(ChatGptModelsEnum.base_models_priority())

    for model_priority in ChatGptModelsEnum.base_models_priority():
        assert model_priorities[model_priority["model"]] == model_priority["priority"]


async def test_update_existing_models(dbsession: Session) -> None:
    ChatGptModelFactory.create_batch(size=3)

    chatgpt_service = ChatGptService.build()

    await chatgpt_service.update_chatgpt_models()

    models = dbsession.query(ChatGptModels).all()

    model_priorities = {model.model: model.priority for model in models}
    assert len(models) == len(ChatGptModelsEnum.base_models_priority())

    for model_priority in ChatGptModelsEnum.base_models_priority():
        assert model_priorities.get(model_priority["model"]) == model_priority["priority"]
