from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID


class Country(BaseModel):
    id: Optional[UUID]
    name: str
    abbreviation: str  # Alpha 2 Country Abbreviation
    flag: HttpUrl
