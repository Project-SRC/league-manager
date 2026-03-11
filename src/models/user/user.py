from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID | None = None


class TokenData(BaseModel):
    username: str = ""


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
    is_manager: bool = False
    is_driver: bool = False
    is_steward: bool = False
    is_admin: bool = False
    manager_id: UUID | None = None
    driver_id: UUID | None = None
    steward_id: UUID | None = None
