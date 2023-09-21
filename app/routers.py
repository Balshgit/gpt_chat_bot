from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from app.api.system.controllers import router as system_router
from settings.config import get_settings

settings = get_settings()

api_router = APIRouter(
    prefix=settings.api_prefix,
    default_response_class=ORJSONResponse,
)


api_router.include_router(system_router, tags=["system"])
