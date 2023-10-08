import factory

from infra.database.db_adapter import Database
from settings.config import settings

database = Database(settings)


class BaseModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_session = database.get_sync_db_session()
