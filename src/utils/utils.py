import re
from typing import Any, NewType, Protocol
from uuid import UUID

from pydantic import BaseModel

from src.db.db import get_connector
from src.models.internal.database import QueryResult
from src.utils.constants import VALID_TIME_REGEX

CustomClass = NewType("CustomClass", BaseModel)


class HasId(Protocol):
    """A protocol for objects that have an 'id' attribute."""

    id: UUID | None


def verify_id(obj: HasId) -> bool:
    """Verify that an object has a valid UUID."""
    return obj.id is not None


async def verify_exists_by_id(identifier: str, table: str):
    """Verify that a record exists by ID."""
    conn = get_connector(legacy=True)
    result: QueryResult = await conn.execute(
        "get", {"table": table, "filters": {"id": identifier}}
    )

    if result.error:
        return False

    if result.data:
        record = result.data[0]
        if (
            record.get("deleted_at") is None
            and record.get("ended_at") is None
            and record.get("terminated_at") is None
            and record.get("deactivated_at") is None
        ):
            return True
    return False


async def get_object_by_id(identifier: str, table: str, record_class: type[BaseModel]):
    """Get an object by ID from the database."""
    conn = get_connector(legacy=True)
    result: QueryResult | Any = await conn.execute(
        "get", {"table": table, "filters": {"id": identifier}}
    )

    if result.error:
        return None

    if result.data:
        record_data = result.data[0]
        if (
            record_data.get("deleted_at") is None
            and record_data.get("ended_at") is None
            and record_data.get("terminated_at") is None
            and record_data.get("deactivated_at") is None
        ):
            try:
                return record_class.model_validate(record_data)
            except Exception:
                return None
    return None


def validated_string_time(time_string: str) -> bool:
    valid = re.compile(VALID_TIME_REGEX)
    return valid.fullmatch(time_string) is None
