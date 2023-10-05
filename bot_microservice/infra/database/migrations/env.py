import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.future import Connection

from infra.database.meta import meta
from infra.utils import load_all_models
from settings.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# for 'autogenerate' support from myapp import mymodel
load_all_models()

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = meta


async def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=str(settings.db_url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Run actual sync migrations.

    :param connection: connection to the database.

    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_async_engine(str(settings.db_url))

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    asyncio.run(run_migrations_offline())
else:
    asyncio.run(run_migrations_online())
