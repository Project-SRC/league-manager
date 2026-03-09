import os
import logging
from functools import lru_cache
from typing import Any

import structlog
from structlog.stdlib import LoggerFactory
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.MOCK: bool = os.getenv("MOCK", "false").lower() == "true"
        self.TEST: bool = os.getenv("TEST", "false").lower() == "true"
        self.VERSION: str = os.getenv("VERSION", "0.0.1-alpha")

        self.SUPABASE_URL: str = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
        self.SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "")
        self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
        )

        self.WS_ADDRESS: str = os.getenv("WS_ADDRESS", "localhost")
        self.WS_PORT: int = int(os.getenv("WS_PORT", "8765"))

        self.RDB_DB: str = os.getenv("RDB_DB", "API")


def setup_logging() -> None:
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
setup_logging()
log = structlog.get_logger()
