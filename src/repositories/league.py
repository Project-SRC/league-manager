from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.schemas.league import League


class LeagueRepository(BaseRepository[League]):
    """Repository for League operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(League, session)

    async def get_by_name(self, name: str) -> League | None:
        """Get league by name."""
        return await self.get_one_by_filters(name=name)

    async def get_active_leagues(self) -> list[League]:
        """Get all active (non-ended) leagues."""
        query = select(self.model).where(self.model.ended_at.is_(None))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_ended_leagues(self) -> list[League]:
        """Get all ended leagues."""
        query = select(self.model).where(self.model.ended_at.isnot(None))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def end_league(self, id: UUID) -> League | None:
        """End a league by setting ended_at."""
        return await self.update(id, ended_at=datetime.now(UTC))
