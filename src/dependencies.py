from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from src.authentication.constants import backend
from src.authentication.dependencies import get_current_user, get_instructor
from src.database import get_session_maker
from src.schemas import FullUser

SessionMaker = Annotated[async_sessionmaker[AsyncSession], Depends(get_session_maker)]
BackendToken = Annotated[str, Depends(backend)]
GetFullUser = Annotated[FullUser, get_current_user]
GetFullInstructor = Annotated[FullUser, get_instructor]
