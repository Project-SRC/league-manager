from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.schemas.league import Race


class RaceRepository(BaseRepository[Race]):
    """Repository for Race operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Race, session)

    async def get_by_track(self, track_id: UUID) -> list[Race]:
        """Get races by track ID."""
        return await self.get_by_filters(track_id=track_id)

    async def get_upcoming_races(self) -> list[Race]:
        """Get upcoming races (future dates)."""
        return await self.get_by_filters()

    async def get_by_date_range(self, start: datetime, end: datetime) -> list[Race]:
        """Get races within a date range."""
        query = select(self.model).where(self.model.date >= start, self.model.date <= end)
        result = await self.session.execute(query)
        return list(result.scalars().all())
