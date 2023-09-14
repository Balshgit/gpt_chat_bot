from typing import NamedTuple


class User(NamedTuple):
    id: int
    is_bot: bool
    first_name: str | None
    last_name: str | None
    username: str | None
    language_code: str


class Chat(NamedTuple):
    id: int
    first_name: str | None
    last_name: str | None
    username: str
    type: str
