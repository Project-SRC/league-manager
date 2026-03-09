from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class Country(BaseModel):
    id: UUID | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: datetime | None = None
    name: str
    abbreviation: str  # Alpha 2 Country Abbreviation
    flag: HttpUrl
