import datetime
from typing import Union

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, MessageType
from sqlalchemy.exc import IntegrityError

from src.authentication.config import mail_conf
from src.authentication.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    LOGIN_ROUTE,
    REGISTRATION_ROUTE,
)
from src.authentication.dependencies import OAuthLoginData
from src.authentication.exceptions import (
    InvalidEmail,
    InvalidResetLink,
    PasswordsDoseNotMatch,
)
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
from src.config import config
from src.dependencies import SessionMaker
from src.exceptions import GlobalException, UnknownError
from src.models import User
from src.schemas import UserFullInfo, UserRole
from src.student.models import Student
from src.student.schemas import StudentDuplicate, StudentInfo, StudentRegisterData

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
        print(row)
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
    REGISTRATION_ROUTE,
    response_model=StudentInfo,
    responses={400: {"model": StudentDuplicate}},
)
async def create_user(data: StudentRegisterData, maker: SessionMaker):
    async with maker.begin() as session:
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
        try:
            session.add(user)
            await session.flush()
            student = Student()
            student.for_user = user.id
            student.student_id = data.student_id
            session.add(student)
        except IntegrityError as error:
            duplicate_field = None
            if "unique constraint" in str(error.orig):
                # Check for a specific constraint name or field in the error message
                if "user_email_key" in str(error.orig):
                    duplicate_field = "email"
                elif "user_username_key" in str(error.orig):
                    duplicate_field = "username"

            # Customize the response message based on the duplicate field
            if duplicate_field:
                message = f"The {duplicate_field} provided is already in use."
            else:
                message = "Duplicate entry detected."
            return JSONResponse(StudentDuplicate(details=message).model_dump(), 400)

        return StudentInfo(
            user=UserFullInfo.model_validate(user), student_id=data.student_id
        )


# Not complete
@router.post("/forgot-password", response_model=ResetedSuccessful)
async def forget_password(
    data: ForgotPasswordData, maker: SessionMaker, request: Request
):
    try:
        async with maker.begin() as session:
            result = await session.execute(
                sa.select(User).where(User.email == data.email)
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise GlobalException(InvalidEmail(), status.HTTP_400_BAD_REQUEST)

            reset_token = await to_async(create_reset_password_token, data.email)

            reset_link = f"https://{config.HOST}:{config.PORT}./{config.FORGOT_PASSWORD_URL}/{reset_token}"
            html = f"<p>{reset_link}</p>"

            message = MessageSchema(
                subject="Reset password instructions",
                recipients=[user.email],
                body=html,
                subtype=MessageType.html,
            )

            fm = FastMail(mail_conf)
            await fm.send_message(message)
            return ResetedSuccessful(message="Email has been sent")
    except Exception:
        raise GlobalException(UnknownError(), status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post(
    "/reset-password",
    response_model=ResetPasswordOut,
    responses={400: {"model": Union[InvalidResetLink, PasswordsDoseNotMatch]}},
)
async def reset_password(data: ResetForegetPasswordData, maker: SessionMaker):
    try:
        email = await to_async(decode_reset_password_token, data.secret_token)
        if email is None:
            raise GlobalException(InvalidResetLink(), status.HTTP_400_BAD_REQUEST)
        if data.new_password != data.confirm_password:
            raise GlobalException(PasswordsDoseNotMatch(), status.HTTP_400_BAD_REQUEST)

        hashed_password = await to_async(hash_password, data.new_password)
        async with maker.begin() as session:
            await session.execute(
                sa.update(User)
                .where(User.email == email)
                .values({"password": hashed_password})
            )
        return ResetPasswordOut()
    except Exception:
        raise GlobalException(UnknownError(), status.HTTP_500_INTERNAL_SERVER_ERROR)
