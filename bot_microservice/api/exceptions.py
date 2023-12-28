from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from api.base_schemas import BaseError, BaseResponse


class BaseAPIException(Exception):
    pass


class InternalServerError(BaseError):
    pass


class InternalServerErrorResponse(BaseResponse):
    error: InternalServerError

    class Config:
        json_schema_extra = {
            "example": {
                "status": 500,
                "error": {
                    "type": "InternalServerError",
                    "title": "Server encountered an unexpected error that prevented it from fulfilling the request",
                    "detail": "error when adding send message",
                },
            },
        }


async def internal_server_error_handler(_request: Request, _exception: Exception) -> ORJSONResponse:
    error = InternalServerError(title="Something went wrong!", type="InternalServerError")
    response = InternalServerErrorResponse(status=500, error=error).model_dump(exclude_unset=True)
    return ORJSONResponse(status_code=500, content=response)
