import pytest
from assertpy import assert_that
from faker import Faker
from httpx import AsyncClient
from sqlalchemy import desc
from sqlalchemy.orm import Session

from core.bot.models.chatgpt import ChatGptModels
from tests.integration.factories.bot import ChatGptModelFactory

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.enable_socket,
]


async def test_get_chatgpt_models(
    dbsession: Session,
    rest_client: AsyncClient,
) -> None:
    model1 = ChatGptModelFactory(priority=0)
    model2 = ChatGptModelFactory(priority=42)
    model3 = ChatGptModelFactory(priority=1)
    response = await rest_client.get(url="/api/chatgpt/models")

    assert response.status_code == 200

    data = response.json()["data"]
    assert_that(data).is_equal_to(
        [
            {
                "id": model2.id,
                "model": model2.model,
                "priority": model2.priority,
            },
            {
                "id": model3.id,
                "model": model3.model,
                "priority": model3.priority,
            },
            {
                "id": model1.id,
                "model": model1.model,
                "priority": model1.priority,
            },
        ]
    )


async def test_change_chatgpt_model_priority(
    dbsession: Session,
    rest_client: AsyncClient,
    faker: Faker,
) -> None:
    model1 = ChatGptModelFactory(priority=0)
    model2 = ChatGptModelFactory(priority=1)
    priority = faker.random_int(min=2, max=7)
    response = await rest_client.put(url=f"/api/chatgpt/models/{model2.id}/priority", json={"priority": priority})
    assert response.status_code == 202

    upd_model1, upd_model2 = dbsession.query(ChatGptModels).order_by(ChatGptModels.priority).all()

    assert model1.model == upd_model1.model
    assert model1.priority == upd_model1.priority
    assert model2.model == upd_model2.model
    assert upd_model2.priority == priority


async def test_reset_chatgpt_models_priority(
    dbsession: Session,
    rest_client: AsyncClient,
) -> None:
    ChatGptModelFactory.create_batch(size=4)
    ChatGptModelFactory(priority=42)

    response = await rest_client.put(url="/api/chatgpt/models/priority/reset")
    assert response.status_code == 202

    models = dbsession.query(ChatGptModels).all()
    assert len(models) == 5

    models = dbsession.query(ChatGptModels).all()

    for model in models:
        assert model.priority == 0


async def test_create_new_chatgpt_model(
    dbsession: Session,
    rest_client: AsyncClient,
    faker: Faker,
) -> None:
    ChatGptModelFactory.create_batch(size=2)
    ChatGptModelFactory(priority=42)

    model_name = "new-gpt-model"
    model_priority = faker.random_int(min=1, max=5)

    models = dbsession.query(ChatGptModels).all()
    assert len(models) == 3

    response = await rest_client.post(
        url="/api/chatgpt/models",
        json={
            "model": model_name,
            "priority": model_priority,
        },
    )
    assert response.status_code == 201

    models = dbsession.query(ChatGptModels).all()
    assert len(models) == 4

    latest_model = dbsession.query(ChatGptModels).order_by(desc(ChatGptModels.id)).limit(1).one()
    assert latest_model.model == model_name
    assert latest_model.priority == model_priority

    assert response.json() == {
        "model": model_name,
        "priority": model_priority,
    }


async def test_add_existing_chatgpt_model(
    dbsession: Session,
    rest_client: AsyncClient,
    faker: Faker,
) -> None:
    ChatGptModelFactory.create_batch(size=2)
    model = ChatGptModelFactory(priority=42)

    model_name = model.model
    model_priority = faker.random_int(min=1, max=5)

    models = dbsession.query(ChatGptModels).all()
    assert len(models) == 3

    response = await rest_client.post(
        url="/api/chatgpt/models",
        json={
            "model": model_name,
            "priority": model_priority,
        },
    )
    assert response.status_code == 201

    models = dbsession.query(ChatGptModels).all()
    assert len(models) == 3


async def test_delete_chatgpt_model(
    dbsession: Session,
    rest_client: AsyncClient,
) -> None:
    ChatGptModelFactory.create_batch(size=2)
    model = ChatGptModelFactory(priority=42)

    models = dbsession.query(ChatGptModels).all()
    assert len(models) == 3

    response = await rest_client.delete(url=f"/api/chatgpt/models/{model.id}")
    assert response.status_code == 204

    models = dbsession.query(ChatGptModels).all()
    assert len(models) == 2

    assert model not in models
