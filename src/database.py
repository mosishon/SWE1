from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker

engine = create_async_engine("")


@lru_cache()
def get_session_maker() -> async_sessionmaker:
    return async_sessionmaker(engine)
