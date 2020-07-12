from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Participation(BaseModel):
    id: Optional[UUID]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: Optional[datetime] = None
    race: UUID
    driver: UUID
