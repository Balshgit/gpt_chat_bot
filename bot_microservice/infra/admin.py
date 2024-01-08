from typing import TYPE_CHECKING

from sqladmin import Admin, ModelView
from sqlalchemy import Select, desc, select
from sqlalchemy.orm import contains_eager, load_only
from starlette.requests import Request

from core.auth.models.users import AccessToken, User, UserQuestionCount
from core.bot.models.chatgpt import ChatGptModels
from core.utils import build_uri
from settings.config import settings

if TYPE_CHECKING:
    from main import Application


class ChatGptAdmin(ModelView, model=ChatGptModels):
    name = "ChatGPT model"
    name_plural = "ChatGPT models"
    column_list = [ChatGptModels.id, ChatGptModels.model, ChatGptModels.priority]
    column_sortable_list = [ChatGptModels.priority]
    column_default_sort = ("priority", True)
    form_widget_args = {"model": {"readonly": True}}

    can_create = False
    can_delete = False


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    column_list = [
        User.id,
        User.username,
        User.first_name,
        User.last_name,
        User.is_active,
        User.ban_reason,
        "question_count",
        "last_question_at",
        User.created_at,
    ]

    column_default_sort = ("created_at", True)
    form_widget_args = {"created_at": {"readonly": True}}

    def list_query(self, request: Request) -> Select[tuple[User]]:
        return (
            select(User)
            .options(
                load_only(
                    User.id,
                    User.username,
                    User.first_name,
                    User.last_name,
                    User.is_active,
                    User.created_at,
                )
            )
            .outerjoin(User.user_question_count)
            .options(
                contains_eager(User.user_question_count).options(
                    load_only(
                        UserQuestionCount.question_count,
                        UserQuestionCount.last_question_at,
                    )
                )
            )
        ).order_by(desc(UserQuestionCount.question_count))


class AccessTokenAdmin(ModelView, model=AccessToken):
    name = "API access token"
    name_plural = "API access tokens"
    column_list = [AccessToken.user_id, "username", AccessToken.token, AccessToken.created_at]
    form_widget_args = {"created_at": {"readonly": True}}


def create_admin(application: "Application") -> Admin:
    admin = Admin(
        title="Chat GPT admin",
        app=application.fastapi_app,
        engine=application.db.async_engine,
        base_url=build_uri([settings.URL_PREFIX, "admin"]),
        authentication_backend=None,
    )
    admin.add_view(ChatGptAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(AccessTokenAdmin)
    return admin
