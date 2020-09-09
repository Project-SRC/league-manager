from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID


class Country(BaseModel):
    id: Optional[UUID]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: Optional[datetime] = None
    name: str
    abbreviation: str  # Alpha 2 Country Abbreviation
    flag: HttpUrl
