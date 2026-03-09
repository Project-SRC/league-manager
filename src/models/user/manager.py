from datetime import datetime
from uuid import UUID

from src.models.user.user import User


class Manager(User):
    id: UUID | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deactivated_at: datetime | None = None
    active: bool = True
