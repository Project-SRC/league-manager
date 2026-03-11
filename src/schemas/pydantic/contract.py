from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateContract(BaseModel):
    """Schema for creating a new contract."""

    team_id: UUID | None = None
    driver_id: UUID | None = None


class UpdateContract(BaseModel):
    """Schema for updating a contract."""

    team_id: UUID | None = None
    driver_id: UUID | None = None
    terminated_at: datetime | None = None


class ContractResponse(BaseModel):
    """Schema for contract responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    team_id: UUID | None = None
    driver_id: UUID | None = None
    terminated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
