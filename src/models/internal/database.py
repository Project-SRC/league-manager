from dataclasses import dataclass
from typing import Any


@dataclass
class QueryResult:
    data: list[dict[str, Any]] | None = None
    count: int | None = None
    error: dict[str, Any] | None = None
