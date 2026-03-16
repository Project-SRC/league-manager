from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.schemas.league import Participation


class ParticipationRepository(BaseRepository[Participation]):
    """Repository for Participation operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Participation, session)

    async def get_by_race(self, race_id: UUID) -> list[Participation]:
        """Get participations by race ID."""
        return await self.get_by_filters(race_id=race_id)

    async def get_by_driver(self, driver_id: UUID) -> list[Participation]:
        """Get participations by driver ID."""
        return await self.get_by_filters(driver_id=driver_id)

    async def get_race_driver_participation(
        self, race_id: UUID, driver_id: UUID
    ) -> Participation | None:
        """Get a specific driver participation in a race."""
        return await self.get_one_by_filters(race_id=race_id, driver_id=driver_id)

    async def get_by_position(self, race_id: UUID, position: int) -> Participation | None:
        """Get participation by race and position."""
        return await self.get_one_by_filters(race_id=race_id, position=position)
