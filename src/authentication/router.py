import datetime

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, status

from src.authentication.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    LOGIN_ROUTE,
    REGISTRATION_ROUTE,
)
from src.authentication.schemas import LoginData, Token, TokenData
from src.authentication.utils import create_access_token, hash_password, to_async
from src.dependencies import SessionMaker
from src.models import User
from src.schemas import UserRole
from src.student.models import Student
from src.student.schemas import StudentInfo, StudentRegisterData

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
            .where(User.password == await to_async(hash_password, data.password))
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


# TODO error handling
@router.post(
    REGISTRATION_ROUTE, status_code=status.HTTP_201_CREATED, response_model=StudentInfo
)
async def create_user(data: StudentRegisterData, maker: SessionMaker):
    async with maker.begin() as session:
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            national_id=data.national_id,
            email=data.email,
            username=data.username,
            phone_number=data.phone_number,
            birth_day=data.birth_day,
            password=await to_async(hash_password, data.password),
            role=UserRole.STUDENT,
        )
        student = Student()
        student.for_user = user.id
        student.student_id = data.student_id
        session.add_all([user, student])
        return StudentInfo.model_validate(user)
