from typing import Any

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

    def table(self, name: str):
        raise NotImplementedError

    async def execute(self, operation: str, payload: dict[str, Any]) -> QueryResult:
        raise NotImplementedError


_connector: DBConnector | None = None


def get_connector(legacy: bool = False) -> DBConnector:
    """Get the database connector implementation.

    Args:
        legacy: If True, use the legacy RethinkDB connector via websocket.
                If False (default), use Supabase.
    """
    global _connector

    if legacy:
        from src.db.legacy import LegacyConnector

        return LegacyConnector()

    if _connector is None:
        from src.db.supabase import SupabaseConnector

        _connector = SupabaseConnector()
    return _connector
