from typing import Any

from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.requests import Request

from api.base_schemas import BaseError, BaseResponse


class BaseAPIException(Exception):
    _content_type: str = "application/json"
    model: type[BaseResponse] = BaseResponse
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    title: str | None = None
    type: str | None = None
    detail: str | None = None
    instance: str | None = None
    headers: dict[str, str] | None = None

    def __init__(self, **ctx: Any) -> None:
        self.__dict__ = ctx

    @classmethod
    def example(cls) -> dict[str, Any] | None:
        if isinstance(cls.model.Config.schema_extra, dict):  # type: ignore[attr-defined]
            return cls.model.Config.schema_extra.get("example")  # type: ignore[attr-defined]
        return None

    @classmethod
    def response(cls) -> dict[str, Any]:
        return {
            "model": cls.model,
            "content": {
                cls._content_type: cls.model.Config.schema_extra,  # type: ignore[attr-defined]
            },
        }


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


class PermissionMissing(BaseError):
    pass


class PermissionMissingResponse(BaseResponse):
    error: PermissionMissing

    class Config:
        json_schema_extra = {
            "example": {
                "status": 403,
                "error": {
                    "type": "PermissionMissing",
                    "title": "Permission required for this endpoint is missing",
                },
            },
        }


class PermissionMissingError(BaseAPIException):
    model = PermissionMissingResponse
    status_code = status.HTTP_403_FORBIDDEN
    title: str = "Permission required for this endpoint is missing"


async def internal_server_error_handler(_request: Request, _exception: Exception) -> ORJSONResponse:
    error = InternalServerError(title="Something went wrong!", type="InternalServerError")
    response = InternalServerErrorResponse(status=500, error=error).model_dump(exclude_unset=True)
    return ORJSONResponse(status_code=500, content=response)
