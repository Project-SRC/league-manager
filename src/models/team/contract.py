from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Contract(BaseModel):
    id: UUID
    created_at: datetime
    terminated_at: Optional[datetime]
    team: UUID
    driver: UUID
