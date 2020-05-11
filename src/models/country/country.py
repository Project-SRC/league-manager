from pydantic import BaseModel, HttpUrl
from uuid import UUID


class Country(BaseModel):
    id: UUID
    name: str
    abbreviation: str  # Alpha 2 Country Abbreviation
    flag: HttpUrl
