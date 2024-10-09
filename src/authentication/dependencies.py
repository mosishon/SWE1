import datetime

import jwt
import sqlalchemy as sa
from fastapi import HTTPException, status
from pydantic import ValidationError

from src.authentication.constants import ALGORITHM
from src.authentication.schemas import TokenData
from src.config import config
from src.dependencies import BackendToken, SessionMaker
from src.models import User
from src.schemas import FullUser


async def get_current_user(maker: SessionMaker, token: BackendToken) -> FullUser:
    try:
        algs = [ALGORITHM]
        payload = jwt.decode(token, config.SECRET, algorithms=algs)
        token_data = TokenData(**payload)

        if datetime.datetime.fromtimestamp(token_data.exp) < datetime.datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    async with maker.begin() as session:
        result = await session.execute(
            sa.select(User).where(User.id == token_data.user_id)
        )
        user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return FullUser.model_validate(user)
