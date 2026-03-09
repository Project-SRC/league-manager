from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Contract(BaseModel):
    id: UUID | None = None
    created_at: datetime = datetime.now()
    terminated_at: datetime | None = None
    team: UUID
    driver: UUID
