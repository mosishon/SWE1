import datetime

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, status

from src.authentication.constants import ACCESS_TOKEN_EXPIRE_MINUTES, LOGIN_ROUTE
from src.authentication.schemas import LoginData, Token, TokenData
from src.authentication.utils import create_access_token, hash_password, to_async
from src.dependencies import SessionMaker
from src.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(LOGIN_ROUTE, response_model=Token)
async def login(data: LoginData, maker: SessionMaker):
    if not data.username:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="username is empty")
    elif not data.password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="password is empty")
    async with maker.begin() as session:
        result = await session.execute(
            sa.select(User.id)
            .where(User.username == data.username)
            .where(User.password == await to_async(hash_password(data.password)))
        )
        uid = result.scalar_one_or_none()
        if uid:
            user_data = {
                "user_id": uid,
                "exp": (
                    datetime.datetime.now()
                    + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                ).timestamp(),
            }

            return await to_async(create_access_token(TokenData(**user_data)))
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="username or password is wrong.",
            )
