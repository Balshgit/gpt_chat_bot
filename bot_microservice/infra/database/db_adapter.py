import os
import pkgutil
from asyncio import current_task
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from settings.config import AppSettings


class Database:
    def __init__(self, settings: AppSettings) -> None:
        self.echo_logs = settings.DB_ECHO
        self.db_file = settings.db_file
        self._async_engine: AsyncEngine = create_async_engine(
            str(settings.async_db_url),
            echo=settings.DB_ECHO,
            execution_options={"isolation_level": "AUTOCOMMIT"},
        )
        self._async_session_factory = async_scoped_session(
            async_sessionmaker(
                autoflush=False,
                class_=AsyncSession,
                expire_on_commit=False,
                bind=self._async_engine,
            ),
            scopefunc=current_task,
        )
        self._sync_engine = create_engine(str(settings.sync_db_url), echo=settings.DB_ECHO)
        self._sync_session_factory = scoped_session(sessionmaker(self._sync_engine))

    def get_sync_db_session(self) -> Session:
        session: Session = self._sync_session_factory()
        try:
            return session
        except Exception as err:
            session.rollback()
            raise err
        finally:
            session.commit()
            session.close()

    @property
    def async_engine(self) -> AsyncEngine:
        return self._async_engine

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._async_session_factory()

        async with session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    @asynccontextmanager
    async def get_transaction_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._async_session_factory() as session, session.begin():
            try:
                yield session
            except Exception as error:
                await session.rollback()
                raise error

    async def create_database(self) -> None:
        """
        Create a test database.

        :param engine: Async engine for database creation
        :param db_path: path to sqlite file

        """
        if not self.db_file.exists():
            from infra.database.meta import meta

            load_all_models()
            try:
                async with self._async_engine.begin() as connection:
                    await connection.run_sync(meta.create_all)

                logger.info("all migrations are applied")
            except Exception as err:
                logger.error("Cant run migrations", err=err)

    async def drop_database(self) -> None:
        """
        Drop current database.

        :param path: Delete sqlite database file

        """
        if self.db_file.exists():
            os.remove(self.db_file)


def load_all_models() -> None:
    """Load all models from this folder."""
    package_dir = Path(__file__).resolve().parent.parent
    package_dir = package_dir.joinpath("core")
    modules = pkgutil.walk_packages(path=[str(package_dir)], prefix="core.")
    models_packages = [module for module in modules if module.ispkg and "models" in module.name]
    for module in models_packages:
        model_pkgs = pkgutil.walk_packages(
            path=[os.path.join(str(module.module_finder.path), "models")], prefix=f"{module.name}."  # type: ignore
        )
        for model_pkg in model_pkgs:
            __import__(model_pkg.name)
