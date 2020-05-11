from datetime import datetime
from src.models.user.user.User
from uuid import UUID


class Manager(User):
    id: UUID
    created_at: datetime
    updated_at: datetime
    active: bool = None
