from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.schemas.track import Track


class TrackRepository(BaseRepository[Track]):
    """Repository for Track operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Track, session)

    async def get_by_name(self, name: str) -> Track | None:
        """Get track by name."""
        return await self.get_one_by_filters(name=name, deleted_at=None)

    async def get_by_country(self, country_id: UUID) -> list[Track]:
        """Get tracks by country ID."""
        return await self.get_by_filters(country_id=country_id, deleted_at=None)

    async def get_by_type(self, track_type: str) -> list[Track]:
        """Get tracks by type (e.g., 'road', 'oval', 'street')."""
        return await self.get_by_filters(type=track_type, deleted_at=None)

    async def get_by_direction(self, direction: str) -> list[Track]:
        """Get tracks by direction (e.g., 'clockwise', 'counterclockwise')."""
        return await self.get_by_filters(direction=direction, deleted_at=None)

    async def get_all_active(self) -> list[Track]:
        """Get all active (non-deleted) tracks."""
        return await self.get_by_filters(deleted_at=None)
