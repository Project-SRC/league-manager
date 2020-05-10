from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    id: UUID
    username: str
    name: str
    disabled: Optional[bool] = None


class UserInDB(User):
    password: str
