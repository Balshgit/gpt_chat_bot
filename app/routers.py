from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from app.api.system.controllers import router as system_router

api_router = APIRouter(prefix='/api', default_response_class=ORJSONResponse)


api_router.include_router(system_router, tags=['system'])
