from __future__ import annotations

from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository[ModelType: Base]:
    """Base repository with common CRUD operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """Get a record by ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ModelType]:
        """Get all records."""
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def get_by_filters(self, **filters: Any) -> list[ModelType]:
        """Get records matching filters."""
        query = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_one_by_filters(self, **filters: Any) -> ModelType | None:
        """Get one record matching filters."""
        query = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, **data: Any) -> ModelType:
        """Create a new record."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: UUID, **data: Any) -> ModelType | None:
        """Update a record by ID."""
        instance = await self.get_by_id(id)
        if instance:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            await self.session.flush()
            await self.session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""
        result = await self.session.execute(delete(self.model).where(self.model.id == id))  # type: ignore[attr-defined]
        await self.session.flush()
        return result.rowcount > 0  # type: ignore[attr-defined]

    async def count(self) -> int:
        """Count all records."""
        result = await self.session.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()
