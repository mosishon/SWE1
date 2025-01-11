import datetime
from typing import Annotated, List

import jwt
import sqlalchemy as sa
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

from src.authentication.constants import ALGORITHM, backend
from src.authentication.schemas import TokenData
from src.config import config
from src.dependencies import SessionMaker
from src.models import Admin
from src.schemas import AdminSchema, UserRole

BackendToken = Annotated[str, Depends(backend)]


# async def get_current_user(maker: SessionMaker, token: BackendToken) -> StudentSchema:
#     try:
#         algs = [ALGORITHM]
#         payload = jwt.decode(token, config.SECRET, algorithms=algs)
#         token_data = TokenData(**payload)

#         if datetime.datetime.fromtimestamp(token_data.exp) < datetime.datetime.now():
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Token expired",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#     except (jwt.InvalidTokenError, ValidationError):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     async with maker.begin() as session:
#         result = await session.execute(
#             sa.select(User).where(User.id == token_data.user_id)
#         )
#         user = result.scalar_one_or_none()

#         if user is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Could not find user",
#             )

#         return FullUser.model_validate(user)


# GetFullUser = Annotated[FullUser, Depends(get_current_user)]


OAuthLoginData = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_current_admin(maker: SessionMaker, token: BackendToken) -> AdminSchema:
    try:
        algs = [ALGORITHM]
        payload = jwt.decode(token, config.SECRET, algorithms=algs)
        token_data = TokenData(**payload)
        if token_data.role != UserRole.ADMIN:
            raise jwt.InvalidTokenError()

        if datetime.datetime.fromtimestamp(token_data.exp) < datetime.datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    async with maker.begin() as session:
        result = await session.execute(
            sa.select(Admin).where(Admin.id == token_data.user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find user",
            )

        return AdminSchema.model_validate(user)


GetFullAdmin = Annotated[AdminSchema, Depends(get_current_admin)]


def _allowed_by(token: BackendToken, allowed_by: List[UserRole]) -> UserRole:
    try:
        algs = [ALGORITHM]
        payload = jwt.decode(token, config.SECRET, algorithms=algs)
        token_data = TokenData(**payload)
        if token_data.role is not None:
            # ADMIN HAS FULL ACCESS
            if allowed_by == UserRole.ALL:
                return token_data.role
            elif token_data.role in allowed_by or token_data.role == UserRole.ADMIN:
                return token_data.role
        raise jwt.InvalidTokenError()

    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )


def allowed_by(allowed_roles: List[UserRole] | UserRole) -> UserRole:
    if isinstance(allowed_roles, list):
        if len(allowed_roles) == 0:
            raise ValueError("at least need 1 role ")
    elif isinstance(allowed_roles, UserRole):
        allowed_roles = [allowed_roles]

    def f(token: BackendToken):
        return _allowed_by(token, allowed_roles)

    return Depends(f)
