import os
from typing import TYPE_CHECKING

from sqladmin import Admin, ModelView

from core.bot.models.chatgpt import ChatGptModels
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
    base_url = os.path.join(settings.URL_PREFIX, "admin")
    admin = Admin(
        title="Chat GPT admin",
        app=application.fastapi_app,
        engine=application.db.async_engine,
        base_url=base_url if base_url.startswith("/") else "/" + base_url,
        authentication_backend=None,
    )
    admin.add_view(ChatGptAdmin)
    return admin
