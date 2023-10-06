from pydantic import BaseModel, ConfigDict, Field


class LightChatGptModel(BaseModel):
    model: str = Field(..., title="Chat Gpt model")
    priority: int = Field(default=0, ge=0, title="Приоритет модели")


class ChatGptModelsPrioritySerializer(BaseModel):
    priority: int = Field(default=0, ge=0, title="Приоритет модели")


class ChatGptModelSerializer(BaseModel):
    id: int = Field(..., gt=0, title="Id модели")
    model: str = Field(..., title="Chat Gpt model")
    priority: int = Field(..., ge=0, title="Приоритет модели")

    model_config = ConfigDict(from_attributes=True)


class GETChatGptModelsSerializer(BaseModel):
    data: list[ChatGptModelSerializer] = Field(..., title="Список всех моделей")

    model_config = ConfigDict(from_attributes=True)
