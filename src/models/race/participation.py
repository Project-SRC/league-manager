from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Participation(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime
    race: UUID
    driver: UUID
