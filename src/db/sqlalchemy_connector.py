from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import log
from src.db.db import DBConnector
from src.db.session import async_session_factory
from src.models.internal.database import QueryResult


class SQLAlchemyConnector(DBConnector):
    """SQLAlchemy implementation of DBConnector using async sessions."""

    def __init__(self):
        self._session_factory = async_session_factory

    async def _get_session(self) -> AsyncSession:
        return self._session_factory()

    async def execute(self, operation: str, payload: dict[str, Any]) -> QueryResult:
        """Execute a database operation using SQLAlchemy."""
        table: str = payload.get("table", "")
        data = payload.get("data", {})
        filters = payload.get("filters", {})

        try:
            async with self._session_factory() as session:
                if operation == "select":
                    return await self._select(session, table, filters)
                elif operation == "insert":
                    return await self._insert(session, table, data)
                elif operation == "update":
                    return await self._update(session, table, data, filters)
                elif operation == "delete":
                    return await self._delete(session, table, filters)
                else:
                    return QueryResult(error={"message": f"Unknown operation: {operation}"})
        except Exception as e:
            log.error("db_operation_error", operation=operation, error=str(e))
            return QueryResult(error={"message": str(e)})

    async def _select(
        self, session: AsyncSession, table: str, filters: dict[str, Any]
    ) -> QueryResult:
        """Execute a select operation."""
        from src.schemas import (
            Contract,
            Country,
            Driver,
            League,
            LeagueDriver,
            LeagueTeam,
            LeagueTrack,
            Manager,
            Participation,
            Race,
            Steward,
            Team,
            Track,
            User,
        )

        table_map = {
            "user": User,
            "driver": Driver,
            "manager": Manager,
            "steward": Steward,
            "country": Country,
            "team": Team,
            "track": Track,
            "league": League,
            "race": Race,
            "contract": Contract,
            "participation": Participation,
            "league_team": LeagueTeam,
            "league_driver": LeagueDriver,
            "league_track": LeagueTrack,
        }

        model = table_map.get(table)
        if not model:
            return QueryResult(error={"message": f"Unknown table: {table}"})

        query = select(model)
        for key, value in filters.items():
            if hasattr(model, key):
                query = query.where(getattr(model, key) == value)

        result = await session.execute(query)
        rows = result.scalars().all()

        data = []
        for row in rows:
            row_dict = {}
            for column in row.__table__.columns:
                val = getattr(row, column.name)
                if hasattr(val, "hex"):
                    val = val.hex()
                row_dict[column.name] = val
            data.append(row_dict)

        return QueryResult(data=data, count=len(data))

    async def _insert(self, session: AsyncSession, table: str, data: dict[str, Any]) -> QueryResult:
        """Execute an insert operation."""
        from src.schemas import (
            Contract,
            Country,
            Driver,
            League,
            LeagueDriver,
            LeagueTeam,
            LeagueTrack,
            Manager,
            Participation,
            Race,
            Steward,
            Team,
            Track,
            User,
        )

        table_map = {
            "user": User,
            "driver": Driver,
            "manager": Manager,
            "steward": Steward,
            "country": Country,
            "team": Team,
            "track": Track,
            "league": League,
            "race": Race,
            "contract": Contract,
            "participation": Participation,
            "league_team": LeagueTeam,
            "league_driver": LeagueDriver,
            "league_track": LeagueTrack,
        }

        model = table_map.get(table)
        if not model:
            return QueryResult(error={"message": f"Unknown table: {table}"})

        instance = model(**data)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)

        row_dict = {}
        for column in instance.__table__.columns:
            val = getattr(instance, column.name)
            if hasattr(val, "hex"):
                val = val.hex()
            row_dict[column.name] = val

        return QueryResult(data=[row_dict], count=1)

    async def _update(
        self,
        session: AsyncSession,
        table: str,
        data: dict[str, Any],
        filters: dict[str, Any],
    ) -> QueryResult:
        """Execute an update operation."""
        from src.schemas import (
            Contract,
            Country,
            Driver,
            League,
            LeagueDriver,
            LeagueTeam,
            LeagueTrack,
            Manager,
            Participation,
            Race,
            Steward,
            Team,
            Track,
            User,
        )

        table_map = {
            "user": User,
            "driver": Driver,
            "manager": Manager,
            "steward": Steward,
            "country": Country,
            "team": Team,
            "track": Track,
            "league": League,
            "race": Race,
            "contract": Contract,
            "participation": Participation,
            "league_team": LeagueTeam,
            "league_driver": LeagueDriver,
            "league_track": LeagueTrack,
        }

        model = table_map.get(table)
        if not model:
            return QueryResult(error={"message": f"Unknown table: {table}"})

        query = update(model)
        for key, value in filters.items():
            if hasattr(model, key):
                query = query.where(getattr(model, key) == value)

        result = await session.execute(query)
        await session.flush()

        return QueryResult(data=[], count=result.rowcount if hasattr(result, "rowcount") else 0)

    async def _delete(
        self, session: AsyncSession, table: str, filters: dict[str, Any]
    ) -> QueryResult:
        """Execute a delete operation."""
        from src.schemas import (
            Contract,
            Country,
            Driver,
            League,
            LeagueDriver,
            LeagueTeam,
            LeagueTrack,
            Manager,
            Participation,
            Race,
            Steward,
            Team,
            Track,
            User,
        )

        table_map = {
            "user": User,
            "driver": Driver,
            "manager": Manager,
            "steward": Steward,
            "country": Country,
            "team": Team,
            "track": Track,
            "league": League,
            "race": Race,
            "contract": Contract,
            "participation": Participation,
            "league_team": LeagueTeam,
            "league_driver": LeagueDriver,
            "league_track": LeagueTrack,
        }

        model = table_map.get(table)
        if not model:
            return QueryResult(error={"message": f"Unknown table: {table}"})

        query = delete(model)
        for key, value in filters.items():
            if hasattr(model, key):
                query = query.where(getattr(model, key) == value)

        result = await session.execute(query)
        await session.flush()

        return QueryResult(data=[], count=result.rowcount if hasattr(result, "rowcount") else 0)
