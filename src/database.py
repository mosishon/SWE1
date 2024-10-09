from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from src.config import config

engine = create_async_engine(
    f"postgresql+asyncpg://{config.postgres_user}:{config.postgres_password}@\
        {config.postgres_host}:{config.postgres_port}/{config.postgres_db}",
    pool_size=20,
    max_overflow=80,
)


@lru_cache()
def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine)
