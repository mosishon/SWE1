from typing import Annotated, List, Literal

import jwt
from fastapi import Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from src import config
from src.authentication.constants import ALGORITHM
from src.authentication.dependencies import BackendToken
from src.authentication.schemas import TokenData
from src.database import get_session_maker
from src.schemas import UserRole

SessionMaker = Annotated[async_sessionmaker[AsyncSession], Depends(get_session_maker)]


async def _allowed_by(
    token: BackendToken, allowed_by: List[UserRole] | Literal["*"]
) -> UserRole:
    try:
        algs = [ALGORITHM]
        payload = jwt.decode(token, config.config.SECRET, algorithms=algs)
        token_data = TokenData(**payload)
        if token_data.role is not None:
            if allowed_by == "*":
                return token_data.role
            elif token_data.role in allowed_by:
                return token_data.role
        raise jwt.InvalidTokenError()

    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


def allowed_by(allowed_roles: List[UserRole] | Literal["*"]):
    if len(allowed_roles) == 0:
        raise ValueError("at least need 1 role ")
    return Depends(lambda token: _allowed_by(token, allowed_roles))
