from typing import Any

from supabase import Client, create_client

from src.config import log, settings
from src.db.db import DBConnector
from src.models.internal.database import QueryResult


class SupabaseConnector(DBConnector):
    """Supabase implementation of DBConnector."""

    def __init__(self):
        if not settings.SUPABASE_KEY:
            log.warning("SUPABASE_KEY not configured, using empty key")
        self._client: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    def table(self, name: str):  # type: ignore
        return self._client.table(name)

    async def execute(self, operation: str, payload: dict[str, Any]) -> QueryResult:
        """Execute a database operation."""
        table: str = payload.get("table", "")
        data = payload.get("data", {})
        filters = payload.get("filters", {})

        try:
            if operation == "select":
                query = self._client.table(table).select("*")
                for key, value in filters.items():
                    query = query.eq(key, value)
                result = query.execute()
                return QueryResult(data=result.data, count=len(result.data))  # type: ignore[arg-type]

            elif operation == "insert":
                result = self._client.table(table).insert(data).execute()
                return QueryResult(data=result.data, count=len(result.data))  # type: ignore[arg-type]

            elif operation == "update":
                query = self._client.table(table).update(data)
                for key, value in filters.items():
                    query = query.eq(key, value)
                result = query.execute()
                return QueryResult(data=result.data, count=len(result.data))  # type: ignore[arg-type]

            elif operation == "delete":
                query = self._client.table(table).delete()
                for key, value in filters.items():
                    query = query.eq(key, value)
                result = query.execute()
                return QueryResult(data=result.data, count=len(result.data))  # type: ignore[arg-type]

            else:
                return QueryResult(error={"message": f"Unknown operation: {operation}"})

        except Exception as e:
            log.error("db_operation_error", operation=operation, error=str(e))
            return QueryResult(error={"message": str(e)})
