import string

import factory
from bot_microservice.tests.integration.factories.models import Chat, User
from faker import Faker

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
