from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.schemas.user import Steward


class StewardRepository(BaseRepository[Steward]):
    """Repository for Steward operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Steward, session)

    async def get_by_user_id(self, user_id: UUID) -> Steward | None:
        """Get steward by user ID."""
        return await self.get_one_by_filters(user_id=user_id)

    async def get_active_stewards(self) -> list[Steward]:
        """Get all active stewards."""
        return await self.get_by_filters(active=True)

    async def deactivate(self, id: UUID) -> Steward | None:
        """Deactivate a steward."""
        return await self.update(id, active=False, deactivated_at=datetime.now(UTC))

    async def reactivate(self, id: UUID) -> Steward | None:
        """Reactivate a steward."""
        return await self.update(id, active=True, deactivated_at=None)
