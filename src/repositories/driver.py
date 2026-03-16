from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.schemas.user import Driver


class DriverRepository(BaseRepository[Driver]):
    """Repository for Driver operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Driver, session)

    async def get_by_user_id(self, user_id: UUID) -> Driver | None:
        """Get driver by user ID."""
        return await self.get_one_by_filters(user_id=user_id, deleted_at=None)

    async def get_by_number(self, number: str) -> Driver | None:
        """Get driver by number."""
        return await self.get_one_by_filters(number=number, deleted_at=None)

    async def get_active_drivers(self) -> list[Driver]:
        """Get all active (non-deleted) drivers."""
        return await self.get_by_filters(deleted_at=None, active=True)

    async def get_by_country(self, country_id: UUID) -> list[Driver]:
        """Get drivers by country."""
        return await self.get_by_filters(country_id=country_id, deleted_at=None)

    async def soft_delete(self, id: UUID) -> Driver | None:
        """Soft delete a driver by setting deleted_at."""
        return await self.update(id, deleted_at=datetime.now(UTC), updated_at=datetime.now(UTC))
