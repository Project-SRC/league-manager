from pydantic.main import ModelMetaclass
from db.db import run
from typing import NewType
from uuid import UUID
import re

VALID_TIME_REGEX = "([0-9]+)?(\\:)?([0-9]{2})?(\\:)?([0-9]{2})\\.([0-9]{3})"

CustomClass = NewType("CustomClass", ModelMetaclass)


def verify_id(obj):
    return obj.id is not None and isinstance(obj.id, UUID)


async def verify_exists_by_id(identifier: str, database: str, table: str):
    operation = "get"
    payload = {"database": database, "table": table, "identifier": identifier}
    database_obj = await run(operation, payload)
    if len(database_obj.get("response_message")) != 0 and (
        database_obj.get("response_message").get("deleted_at", False) is None
        or database_obj.get("response_message").get("ended_at", False) is None
        or database_obj.get("response_message").get("terminated_at", False) is None
        or database_obj.get("response_message").get("deactivated_at", False) is None
    ):
        return True
    else:
        return False


async def get_object_by_id(
    identifier: str, database: str, table: str, record: CustomClass
):
    operation = "get"
    payload = {"database": database, "table": table, "identifier": identifier}
    database_obj = await run(operation, payload)
    if len(database_obj.get("response_message")) != 0 and (
        database_obj.get("response_message").get("deleted_at", False) is None
        or database_obj.get("response_message").get("ended_at", False) is None
        or database_obj.get("response_message").get("terminated_at", False) is None
        or database_obj.get("response_message").get("deactivated_at", False) is None
    ):
        try:
            obj = record.parse_obj(database_obj.get("response_message"))
        except Exception:
            return None
        else:
            return obj
    else:
        return False


def validated_string_time(time_string: str) -> bool:
    # Compile regex and try to full match the string
    # if it's not a full match it will return None
    # then add a statment to check if it's none to return
    # the string validity
    valid = re.compile(VALID_TIME_REGEX)
    return valid.fullmatch(time_string) is None
