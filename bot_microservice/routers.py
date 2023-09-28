from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from api.bot.controllers import router as bot_router
from api.system.controllers import router as system_router
from settings.config import settings

api_router = APIRouter(
    prefix=settings.api_prefix,
    default_response_class=ORJSONResponse,
)


api_router.include_router(system_router, tags=["system"])
api_router.include_router(bot_router, tags=["bot"])
