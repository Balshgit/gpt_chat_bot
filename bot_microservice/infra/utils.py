import os
import pkgutil
from pathlib import Path

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine


async def create_database(engine: AsyncEngine, db_path: Path) -> None:
    """
    Create a test database.

    :param engine: Async engine for database creation
    :param db_path: path to sqlite file

    """
    if not db_path.exists():
        from infra.database.meta import meta

        load_all_models()
        try:
            async with engine.begin() as connection:
                await connection.run_sync(meta.create_all)

            logger.info("all migrations are applied")
        except Exception as err:
            logger.error("Cant run migrations", err=err)


async def drop_database(path: Path) -> None:
    """
    Drop current database.

    :param path: Delete sqlite database file

    """
    if path.exists():
        os.remove(path)


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
