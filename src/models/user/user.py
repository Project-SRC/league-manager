from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID | None = None


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    id: UUID | None = None
    username: str
    password: str
    name: str
    nickname: str | None = None
    email: str
    profile_picture: HttpUrl | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: datetime | None = None
    is_manager: bool = None
    is_driver: bool = None
    is_steward: bool = None
    is_admin: bool = None
    manager_id: UUID | None = None
    driver_id: UUID | None = None
    steward_id: UUID | None = None
