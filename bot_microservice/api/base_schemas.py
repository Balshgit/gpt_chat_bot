from typing import Any

from fastapi import status as status_code
from pydantic import BaseModel, Field


class BaseError(BaseModel):
    """Error response as defined in
    https://datatracker.ietf.org/doc/html/rfc7807.

    One difference is that the member "type" is not a URI
    """

    type: str | None = Field(title="The name of the class of the error")
    title: str | None = Field(
        title="A short, human-readable summary of the problem that does not change from occurence to occurence",
    )
    detail: str | None = Field(title="А human-readable explanation specific to this occurrence of the problem")
    instance: Any | None = Field(title="Identifier for this specific occurrence of the problem")


class BaseResponse(BaseModel):
    status: int = Field(..., title="Status code of request.", example=status_code.HTTP_200_OK)  # type: ignore[call-arg]
    error: dict[Any, Any] | BaseError | None = Field(None, title="Errors")
    payload: Any | None = Field({}, title="Payload data.")
