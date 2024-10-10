import asyncio
from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from src.config import config
from src.models import BaseModel

URI = f"postgresql+asyncpg://{config.postgres_user}:{config.postgres_password}@\
{config.postgres_host}:{config.postgres_port}/{config.postgres_db}"

print(URI)
engine = create_async_engine(
    URI,
    pool_size=20,
    max_overflow=80,
)


@lru_cache()
def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine)


async def main_run():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


asyncio.create_task(main_run())
