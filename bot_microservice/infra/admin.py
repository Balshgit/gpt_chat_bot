from typing import TYPE_CHECKING

from sqladmin import Admin, ModelView

from core.bot.models.chatgpt import ChatGptModels
from core.utils import build_uri
from settings.config import settings

if TYPE_CHECKING:
    from main import Application


class ChatGptAdmin(ModelView, model=ChatGptModels):
    column_list = [ChatGptModels.id, ChatGptModels.model, ChatGptModels.priority]
    column_sortable_list = [ChatGptModels.priority]
    column_default_sort = ("priority", True)
    form_widget_args = {"model": {"readonly": True}}

    can_create = False
    can_delete = False


def create_admin(application: "Application") -> Admin:
    admin = Admin(
        title="Chat GPT admin",
        app=application.fastapi_app,
        engine=application.db.async_engine,
        base_url=build_uri([settings.URL_PREFIX, "admin"]),
        authentication_backend=None,
    )
    admin.add_view(ChatGptAdmin)
    return admin
