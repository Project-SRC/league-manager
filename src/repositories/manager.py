from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.schemas.user import Manager


class ManagerRepository(BaseRepository[Manager]):
    """Repository for Manager operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Manager, session)

    async def get_by_user_id(self, user_id: UUID) -> Manager | None:
        """Get manager by user ID."""
        return await self.get_one_by_filters(user_id=user_id)

    async def get_active_managers(self) -> list[Manager]:
        """Get all active managers."""
        return await self.get_by_filters(active=True)

    async def deactivate(self, id: UUID) -> Manager | None:
        """Deactivate a manager."""
        return await self.update(id, active=False, deactivated_at=datetime.now(UTC))

    async def reactivate(self, id: UUID) -> Manager | None:
        """Reactivate a manager."""
        return await self.update(id, active=True, deactivated_at=None)
