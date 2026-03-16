from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.schemas.country import Country


class CountryRepository(BaseRepository[Country]):
    """Repository for Country operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Country, session)

    async def get_by_name(self, name: str) -> Country | None:
        """Get country by name."""
        return await self.get_one_by_filters(name=name, deleted_at=None)

    async def get_by_abbreviation(self, abbreviation: str) -> Country | None:
        """Get country by abbreviation."""
        return await self.get_one_by_filters(abbreviation=abbreviation, deleted_at=None)

    async def get_all_active(self) -> list[Country]:
        """Get all active (non-deleted) countries."""
        return await self.get_by_filters(deleted_at=None)
