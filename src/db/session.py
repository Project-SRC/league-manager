from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from urllib.parse import parse_qs, urlparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.schemas import Base

url = settings.DATABASE_URL
parsed = urlparse(url)
query_params = parse_qs(parsed.query)

connect_args = {"ssl": None}
if "sslmode" in query_params:
    mode = query_params["sslmode"][0]
    if mode == "disable":
        connect_args["ssl"] = False

url_without_ssl = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

engine = create_async_engine(
    url_without_ssl,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=connect_args,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
