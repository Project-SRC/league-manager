from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.schemas.user import User


class UserRepository(BaseRepository[User]):
    """Repository for User operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        return await self.get_one_by_filters(username=username, deleted_at=None)

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return await self.get_one_by_filters(email=email)

    async def get_active_users(self) -> list[User]:
        """Get all active (non-deleted) users."""
        return await self.get_by_filters(deleted_at=None)

    async def soft_delete(self, id: UUID) -> User | None:
        """Soft delete a user by setting deleted_at."""
        return await self.update(id, deleted_at=datetime.now(UTC), updated_at=datetime.now(UTC))

    async def create_user(
        self,
        username: str,
        password: str,
        name: str,
        email: str,
        **kwargs,
    ) -> User:
        """Create a new user."""
        return await self.create(
            username=username,
            password=password,
            name=name,
            email=email,
            **kwargs,
        )
