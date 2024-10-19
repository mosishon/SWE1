import datetime

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, Request, status

from src.authentication.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    LOGIN_ROUTE,
    REGISTRATION_ROUTE,
)
from src.authentication.dependencies import OAuthLoginData
from src.authentication.schemas import (
    ForgotPasswordData,
    ResetedSuccessful,
    ResetForegetPasswordData,
    ResetPasswordOut,
    Token,
    TokenData,
)
from src.authentication.utils import (
    create_access_token,
    create_reset_password_token,
    decode_reset_password_token,
    hash_password,
    to_async,
    verify_pwd,
)
from src.dependencies import SessionMaker
from src.models import User
from src.schemas import UserFullInfo, UserRole
from src.student.schemas import StudentInfo, StudentRegisterData

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(LOGIN_ROUTE, response_model=Token)
async def login(data: OAuthLoginData, maker: SessionMaker):
    if not data.username:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="username is empty")
    elif not data.password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="password is empty")
    async with maker.begin() as session:
        result = await session.execute(
            sa.select(User.id, User.password).where(User.username == data.username)
        )
        row = result.first()
        if row and await to_async(verify_pwd, data.password, row[1]):
            user_data = {
                "user_id": row[0],
                "exp": (
                    datetime.datetime.now()
                    + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                ).timestamp(),
            }

            return await to_async(create_access_token, TokenData(**user_data))
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
    async with maker.begin() as _:
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            national_id=data.national_id,
            email=data.email,
            username=data.student_id,
            phone_number=data.phone_number,
            birth_day=data.birth_day,
            password=await to_async(hash_password, data.national_id),
            role=UserRole.STUDENT,
        )

        # TODO request should send to admin for accept

        # session.add(user)
        # await session.flush()
        # student = Student()
        # student.for_user = user.id
        # student.student_id = data.student_id
        # session.add(student)

        return StudentInfo(
            user=UserFullInfo.model_validate(user), student_id=data.student_id
        )


# Not complete
@router.post("/forgot-password", response_model=ResetedSuccessful)
async def forget_password(
    data: ForgotPasswordData, maker: SessionMaker, request: Request
):
    try:
        # Correct it later
        async with maker.begin() as session:
            result = await session.execute(
                sa.select(User).where(User.email == data.email)
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Email address",
                )

            reset_token = await to_async(create_reset_password_token, user.email)

            # TODO send using SMTP to user.email
            reset_link = f"https://xxxxx.xxx/xxxx/{reset_token}"  #
            return ResetedSuccessful(
                message="Email has been sent link", reset_link=reset_link
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something Unexpected, Server Error",
        )


# Query need to be handled
@router.post("/reset-password", response_model=ResetPasswordOut)
async def reset_password(data: ResetForegetPasswordData, maker: SessionMaker):
    try:
        email = await to_async(decode_reset_password_token, data.secret_token)
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Password Reset Payload or Reset Link Expired",
            )
        if data.new_password != data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password and confirm password are not same.",
            )

        hashed_password = await to_async(hash_password, data.new_password)
        async with maker.begin() as session:
            await session.execute(
                sa.update(User)
                .where(User.email == email)
                .values({"password": hashed_password})
            )
        return ResetPasswordOut(success=True, message="Password Rest Successfully!")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something unexpected happened!",
        )
