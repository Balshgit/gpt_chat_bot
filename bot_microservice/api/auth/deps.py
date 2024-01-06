from fastapi import Depends

from api.deps import get_database
from core.auth.repository import UserRepository
from core.auth.services import UserService
from infra.database.db_adapter import Database


def get_user_repository(db: Database = Depends(get_database)) -> UserRepository:
    return UserRepository(db=db)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository=user_repository)
