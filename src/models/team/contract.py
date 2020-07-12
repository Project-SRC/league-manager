from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Contract(BaseModel):
    id: Optional[UUID]
    created_at: datetime = datetime.now()
    terminated_at: Optional[datetime] = None
    team: UUID
    driver: UUID
