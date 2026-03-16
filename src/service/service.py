import os
from collections.abc import Callable
from typing import Any

from dotenv import load_dotenv

VARIABLES = [
    "MOCK",
    "TEST",
    "VERSION",
    "WS_ADDRESS",
    "WS_PORT",
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "RDB_DB",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
]


def get_variable(
    name: str | None = None,
    func: Callable[[Any], Any] | None = None,
) -> Any:
    load_dotenv()

    if name not in VARIABLES:
        return None
    if name:
        value = os.environ.get(name)
        if func:
            return func(value)
        return value
    return {var: os.environ.get(var) for var in VARIABLES}
