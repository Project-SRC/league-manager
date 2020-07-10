from datetime import date, datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    id: Optional[UUID]
    username: str
    password: str
    name: str
    nickname: Optional[str]
    email: str
    profile_picture: Optional[HttpUrl] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime = None
    is_manager: bool = None
    is_driver: bool = None
    is_steward: bool = None
    is_admin: bool = None
    manager_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    steward_id: Optional[UUID] = None
