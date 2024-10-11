from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from src.database import get_session_maker

SessionMaker = Annotated[async_sessionmaker[AsyncSession], Depends(get_session_maker)]
