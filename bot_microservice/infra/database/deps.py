from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from settings.config import settings


@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    engine = create_engine(str(settings.sync_db_url), echo=settings.DB_ECHO)
    session_factory = sessionmaker(engine)
    try:
        yield session_factory()
    finally:
        engine.dispose()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_engine = create_async_engine(
        str(settings.async_db_url),
        echo=settings.DB_ECHO,
        execution_options={"isolation_level": "AUTOCOMMIT"},
    )
    async_session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    try:
        async with async_session_maker() as session:
            yield session
    finally:
        await async_engine.dispose()
