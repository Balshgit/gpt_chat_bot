from dataclasses import dataclass

from infra.database.db_adapter import Database
from settings.config import AppSettings


@dataclass
class UserRepository:
    settings: AppSettings
    db: Database
