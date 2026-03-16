from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.schemas.team import Team


class TeamRepository(BaseRepository[Team]):
    """Repository for Team operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Team, session)

    async def get_by_name(self, name: str) -> Team | None:
        """Get team by name."""
        return await self.get_one_by_filters(name=name, deleted_at=None)

    async def get_active_teams(self) -> list[Team]:
        """Get all active (non-deleted) teams."""
        return await self.get_by_filters(deleted_at=None, active=True)

    async def get_by_team_chief(self, team_chief: UUID) -> list[Team]:
        """Get teams by team chief user ID."""
        return await self.get_by_filters(team_chief=team_chief, deleted_at=None)

    async def soft_delete(self, id: UUID) -> Team | None:
        """Soft delete a team by setting deleted_at."""
        return await self.update(id, deleted_at=datetime.now(UTC), updated_at=datetime.now(UTC))
