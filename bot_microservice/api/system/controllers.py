from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from starlette import status

router = APIRouter()


@router.get(
    "/healthcheck",
    name="system:healthcheck",
    status_code=status.HTTP_200_OK,
    summary="Healthcheck service",
)
async def healthcheck() -> ORJSONResponse:
    return ORJSONResponse(content=None, status_code=status.HTTP_200_OK)
