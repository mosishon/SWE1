import asyncio
import datetime
import os
from functools import lru_cache

import sqlalchemy
import sqlalchemy.exc
from sqlalchemy import insert, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from src.authentication.utils import hash_password, to_async
from src.config import config
from src.models import Admin, BaseModel

URI = os.environ.get(
    "DATABASE_URL"
)  # For Docker (Connection to databse in docker is different with local system)
DB_NAME = os.environ.get("DB_NAME", config.postgres_db)
if URI is None:
    URI = f"postgresql+asyncpg://{config.postgres_user}:{config.postgres_password}@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}"


engine = create_async_engine(URI, pool_size=20, max_overflow=80, echo=True)


@lru_cache()
def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine)


async def main_run():
    async with engine.connect() as conn:
        conn = await conn.execution_options(
            isolation_level="AUTOCOMMIT"
        )  # Disable transaction
        try:
            await conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
            print(f"Database '{DB_NAME}' created.")
        except Exception as e:
            if "already exists" in str(e):
                print(f"Database '{DB_NAME}' already exists.")
            else:
                print(f"Error: {e}")

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
        print("DATABASE Created")
    async with engine.begin() as conn:
        try:
            await conn.execute(
                insert(Admin).values(
                    {
                        "first_name": "admin",
                        "last_name": "admin por",
                        "national_id": "3490595959",
                        "email": "admin@admin.com",
                        "username": "admin",
                        "phone_number": "09120000000",
                        "birth_day": datetime.date(2020, 10, 10),
                        "password": await to_async(hash_password, "admin"),
                    }
                )
            )
        except sqlalchemy.exc.IntegrityError:
            pass


asyncio.create_task(main_run())
