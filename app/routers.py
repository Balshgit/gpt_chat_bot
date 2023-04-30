from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

api_router = APIRouter(prefix="/api", default_response_class=ORJSONResponse)
