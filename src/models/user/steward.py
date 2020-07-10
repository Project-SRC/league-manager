from datetime import datetime
from src.models.user.user import User
from typing import Optional
from uuid import UUID


class Steward(User):
    id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    active: bool = None
