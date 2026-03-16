import os
from functools import lru_cache
from typing import Any

import structlog
from dotenv import load_dotenv


class Settings:
    def __init__(self) -> None:
        # Delay reading environment to initialization
        load_dotenv()
        self.MOCK: bool = os.getenv("MOCK", "false").lower() == "true"
        self.TEST: bool = os.getenv("TEST", "false").lower() == "true"
        self.LEGACY: bool = os.getenv("LEGACY", "false").lower() == "true"
        self.VERSION: str = os.getenv("VERSION", "0.0.1-alpha")

        self.SUPABASE_URL: str = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
        self.SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
        self.SUPABASE_HOST: str = os.getenv("SUPABASE_HOST", "127.0.0.1")
        self.SUPABASE_PORT: int = int(os.getenv("SUPABASE_PORT", "54323"))

        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres?sslmode=disable",
        )

        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "")
        self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
        )

        self.WS_ADDRESS: str = os.getenv("WS_ADDRESS", "localhost")
        self.WS_PORT: int = int(os.getenv("WS_PORT", "8765"))

        self.RDB_DB: str = os.getenv("RDB_DB", "API")


def setup_logging() -> None:
    """Configures logging using structlog for structured, context-aware logging."""

    def extract_details(logger, method_name, event_dict):
        """Extract 'details' from event dict to be a top-level key."""
        if "details" in event_dict:
            details = event_dict.pop("details")
            event_dict["details"] = details
        return event_dict

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        extract_details,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=shared_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
setup_logging()
log = structlog.get_logger()
