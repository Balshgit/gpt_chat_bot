import string
import time
from typing import Any

import factory
import factory.fuzzy
from faker import Faker

from constants import BotStagesEnum
from tests.integration.factories.models import Chat, User

faker = Faker("ru_RU")


class BotUserFactory(factory.Factory):
    id = factory.Sequence(lambda n: 1000 + n)
    is_bot = False
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = faker.profile(fields=["username"])["username"]
    language_code = "ru"

    class Meta:
        model = User


class BotChatFactory(factory.Factory):
    id = factory.Sequence(lambda n: 1 + n)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = faker.profile(fields=["username"])["username"]
    type = "private"

    class Meta:
        model = Chat


class BotInfoFactory(factory.DictFactory):
    token = factory.Faker(
        "bothify", text="#########:??????????????????????????-#????????#?", letters=string.ascii_letters
    )  # example: 579694714:AAFpK8w6zkkUrD4xSeYwF3MO8e-4Grmcy7c
    payment_provider_token = factory.Faker(
        "bothify", text="#########:TEST:????????????????", letters=string.ascii_letters
    )  # example: 579694714:TEST:K8w6zkkUrD4xSeYw
    chat_id = factory.Faker("random_int", min=10**8, max=10**9 - 1)
    super_group_id = factory.Faker("random_int", min=-(10**12) - 10**9, max=-(10**12))  # -1001838004577
    forum_group_id = factory.Faker("random_int", min=-(10**12) - 10**9, max=-(10**12))
    channel_name = factory.Faker("name")
    channel_id = factory.LazyAttribute(lambda obj: f"@{obj.channel_name}")
    name = factory.Faker("name")
    fake_username = factory.Faker("name")
    username = factory.LazyAttribute(lambda obj: "_".join(f"@{obj.fake_username}".split(" ")))  # @Peter_Parker

    class Meta:
        exclude = ("channel_name", "fake_username")


class BotEntitleFactory(factory.DictFactory):
    type = "bot_command"
    offset = 0
    length = 7


class BotMessageFactory(factory.DictFactory):
    message_id = factory.Faker("random_int", min=10**8, max=10**9 - 1)
    chat = factory.LazyFunction(lambda: BotChatFactory()._asdict())
    date = time.time()
    text = factory.Faker("text")
    entities = factory.LazyFunction(lambda: [BotEntitleFactory()])

    @classmethod
    def create_instance(cls, **kwargs: Any) -> dict[str, Any]:
        data = {**cls.build(**kwargs), "from": BotUserFactory()._asdict()}
        return data


class BotUpdateFactory(factory.DictFactory):
    update_id = factory.Faker("random_int", min=10**8, max=10**9 - 1)
    message = factory.LazyFunction(lambda: BotMessageFactory.create_instance())


class CallBackFactory(factory.DictFactory):
    id = factory.Faker("bothify", text="###################")
    chat_instance = factory.Faker("bothify", text="###################")
    message = factory.LazyFunction(lambda: BotMessageFactory.create_instance())
    data = factory.fuzzy.FuzzyChoice(BotStagesEnum)

    @classmethod
    def create_instance(cls, **kwargs: Any) -> dict[str, Any]:
        data = {**cls.build(**kwargs), "from": BotUserFactory()._asdict()}
        return data


class BotCallBackQueryFactory(factory.DictFactory):
    update_id = factory.Faker("random_int", min=10**8, max=10**9 - 1)
    callback_query = factory.LazyFunction(lambda: BotMessageFactory.create_instance())
