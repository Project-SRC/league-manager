from datetime import datetime
from models.user.user import User
from typing import Optional
from uuid import UUID


class Manager(User):
    id: Optional[UUID]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deactivated_at: Optional[datetime] = None
    active: bool = None
