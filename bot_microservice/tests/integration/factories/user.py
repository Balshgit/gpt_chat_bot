import uuid

import factory

from core.auth.models.users import AccessToken, User
from tests.integration.factories.utils import BaseModelFactory


class UserFactory(BaseModelFactory):
    id = factory.Sequence(lambda n: n + 1)
    email = factory.Faker("email")
    username = factory.Faker("user_name", locale="en")
    first_name = factory.Faker("word")
    last_name = factory.Faker("word")
    ban_reason = factory.Faker("text", max_nb_chars=100)
    hashed_password = factory.Faker("word")
    is_active = True
    is_superuser = False
    created_at = factory.Faker("past_datetime")

    class Meta:
        model = User


class AccessTokenFactory(BaseModelFactory):
    user_id = factory.Sequence(lambda n: n + 1)
    token = factory.LazyAttribute(lambda o: str(uuid.uuid4()))
    created_at = factory.Faker("past_datetime")

    class Meta:
        model = AccessToken
