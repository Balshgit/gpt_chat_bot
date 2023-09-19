import pytest
from httpx import AsyncClient

pytestmark = [
    pytest.mark.asyncio,
]


async def test_bot_updates(rest_client: AsyncClient) -> None:
    response = await rest_client.get("/api/healthcheck")

    assert response.status_code == 200
