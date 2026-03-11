from typing import Any

from src.config import settings
from src.models.internal.database import QueryResult


class DBConnector:
    """Interface for database operations.

    Implementations should provide:
    - table(name): returns a table reference
    - select(columns): returns records
    - insert(data): inserts record(s)
    - update(data): updates record(s)
    - delete(): deletes record(s)
    """

    def table(self, name: str) -> str:
        raise NotImplementedError

    async def execute(self, operation: str, payload: dict[str, Any]) -> QueryResult:
        raise NotImplementedError


_connector: DBConnector | None = None


def get_connector() -> DBConnector:
    """Get the database connector implementation based on LEGACY setting.

    If LEGACY=true, use the legacy RethinkDB connector via websocket.
    If LEGACY=false (default), use SQLAlchemy with asyncpg.
    """
    global _connector

    if settings.LEGACY:
        from src.db.legacy import LegacyConnector

        return LegacyConnector()

    if _connector is None:
        from src.db.sqlalchemy_connector import SQLAlchemyConnector

        _connector = SQLAlchemyConnector()
    return _connector
