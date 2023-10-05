from sqlalchemy import Table
from sqlalchemy.orm import as_declarative, declared_attr

from infra.database.meta import meta


@as_declarative(metadata=meta)
class Base:
    """
    Base for all models.

    It has some type definitions to
    enhance autocompletion.
    """

    # Generate __tablename__ automatically
    @declared_attr  # type: ignore[arg-type]
    def __tablename__(self) -> str:
        return self.__name__.lower()  # type: ignore[attr-defined]

    __table__: Table

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        try:
            return f"{self.__class__.__name__}(id={self.id})"  # type: ignore[attr-defined]
        except AttributeError:
            return super().__repr__()
