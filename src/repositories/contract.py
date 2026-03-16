from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.schemas.team import Contract


class ContractRepository(BaseRepository[Contract]):
    """Repository for Contract operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Contract, session)

    async def get_by_driver(self, driver_id: UUID) -> list[Contract]:
        """Get contracts by driver ID."""
        return await self.get_by_filters(driver_id=driver_id)

    async def get_by_team(self, team_id: UUID) -> list[Contract]:
        """Get contracts by team ID."""
        return await self.get_by_filters(team_id=team_id)

    async def get_active_contracts(self) -> list[Contract]:
        """Get all active (non-terminated) contracts."""
        return await self.get_by_filters(terminated_at=None)

    async def get_driver_active_contract(self, driver_id: UUID) -> Contract | None:
        """Get active contract for a driver."""
        return await self.get_one_by_filters(driver_id=driver_id, terminated_at=None)

    async def get_team_active_contracts(self, team_id: UUID) -> list[Contract]:
        """Get active contracts for a team."""
        return await self.get_by_filters(team_id=team_id, terminated_at=None)

    async def terminate(self, id: UUID, terminated_at: date | None = None) -> Contract | None:
        """Terminate a contract."""
        if terminated_at is None:
            terminated_at = date.today()
        return await self.update(id, terminated_at=terminated_at)
