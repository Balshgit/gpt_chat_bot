from dataclasses import dataclass

from core.auth.repositories import UserRepository


@dataclass
class UserService:
    repository: UserRepository
