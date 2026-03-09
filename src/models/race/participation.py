from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Participation(BaseModel):
    id: UUID | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: datetime | None = None
    race: UUID
    driver: UUID
