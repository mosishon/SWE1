import datetime
from typing import Annotated

import jwt
import sqlalchemy as sa
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

from src.authentication.constants import ALGORITHM, backend
from src.authentication.exceptions import NoAccess
from src.authentication.schemas import TokenData
from src.config import config
from src.dependencies import SessionMaker
from src.exceptions import GlobalException
from src.models import User
from src.schemas import FullAdmin, FullUser, UserRole

BackendToken = Annotated[str, Depends(backend)]


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


GetFullUser = Annotated[FullUser, Depends(get_current_user)]


OAuthLoginData = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_admin(maker: SessionMaker, full_user: GetFullUser) -> FullAdmin:
    async with maker.begin() as session:
        result = await session.execute(
            sa.select(User.id)
            .where(User.id == full_user.id)
            .where(User.role == UserRole.ADMIN)
        )
        admin_user = result.first()
        if admin_user is not None:
            return FullAdmin(full_user=full_user)
        else:
            raise GlobalException(NoAccess(), status.HTTP_403_FORBIDDEN)


GetFullAdmin = Annotated[FullAdmin, Depends(get_admin)]
