import time

import factory
from faker import Faker

from tests.integration.factories.models import Chat, User

data = {
    "update_id": 957250703,
    "message": {
        "message_id": 417070387,
        "from": {
            "id": 1000,
            "is_bot": "false",
            "first_name": "William",
            "last_name": "Dalton",
            "username": "bolshakovfortunat",
            "language_code": "ru",
        },
        "chat": {"id": 1, "first_name": "Gabrielle", "last_name": "Smith", "username": "arefi_2019", "type": "private"},
        "date": time.time(),
        "text": "/chatid",
        "entities": [{"type": "bot_command", "offset": 0, "length": 7}],
    },
}


faker = Faker("ru_RU")


class DeleteUserFactory(factory.Factory):
    id = factory.Sequence(lambda n: 1000 + n)
    is_bot = False
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = faker.profile(fields=["username"])["username"]
    language_code = "ru"

    class Meta:
        model = User


class ChatFactory(factory.Factory):
    id = factory.Sequence(lambda n: 1 + n)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = faker.profile(fields=["username"])["username"]
    type = "private"

    class Meta:
        model = Chat
