import datetime
from typing import Union

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, status
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
from src.instructor.models import Instructor
from src.models import Admin
from src.schemas import UserRole
from src.student.exceptions import StudentDuplicate
from src.student.models import Student
from src.student.schemas import StudentAdded, StudentRegisterData, StudentSchema

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(LOGIN_ROUTE, response_model=Token)
async def login(data: OAuthLoginData, maker: SessionMaker):
    if not data.username:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="username is empty")
    elif not data.password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="password is empty")
    async with maker.begin() as session:
        stres = await session.execute(
            sa.select(Student).where(Student.username == data.username)
        )
        adres = await session.execute(
            sa.select(Admin).where(Admin.username == data.username)
        )
        insres = await session.execute(
            sa.select(Instructor).where(Instructor.username == data.username)
        )
        row = stres.scalar()
        adrow = adres.scalar()
        insres = insres.scalar()
        if row and await to_async(verify_pwd, data.password, row.password):
            user_data = {
                "user_id": row.id,
                "role": UserRole.STUDENT,
                "exp": (
                    datetime.datetime.now()
                    + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                ).timestamp(),
            }

            return await to_async(create_access_token, TokenData(**user_data))
        elif adrow and await to_async(verify_pwd, data.password, adrow.password):
            user_data = {
                "user_id": adrow.id,
                "role": UserRole.ADMIN,
                "exp": (
                    datetime.datetime.now()
                    + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                ).timestamp(),
            }

            return await to_async(create_access_token, TokenData(**user_data))
        elif insres and await to_async(verify_pwd, data.password, insres.password):
            user_data = {
                "user_id": insres.id,
                "role": UserRole.INSTRUCTOR,
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
    responses={400: {"model": StudentDuplicate}},
)
async def create_user(data: StudentRegisterData, maker: SessionMaker) -> StudentAdded:
    async with maker.begin() as session:
        # TODO request should send to admin for accept
        try:
            res = (
                await session.execute(
                    sa.insert(Student)
                    .values(
                        {
                            "first_name": data.first_name,
                            "id": data.student_id,
                            "last_name": data.last_name,
                            "national_id": data.national_id,
                            "email": data.email,
                            "username": data.student_id,
                            "phone_number": data.phone_number,
                            "birth_day": data.birth_day,
                            "password": await to_async(hash_password, data.national_id),
                        }
                    )
                    .returning(Student)
                )
            ).scalar()
            if res:
                return StudentAdded(student=StudentSchema.model_validate(res))
            else:
                raise GlobalException(UnknownError(), 500)

        except IntegrityError as error:
            duplicate_fields = []
            if "unique constraint" in str(error.orig):
                s = str(error.orig).find("(") + 1
                e = str(error.orig).find(")")
                duplicate_fields = [i.strip() for i in str(error.orig)[s:e].split(",")]

                # # Check for a specific constraint name or field in the error message
                # if "user_email_key" in str(error.orig):
                #     duplicate_field = "email"
                # elif "user_username_key" in str(error.orig):
                #     duplicate_field = "username"
                # elif "user_phone_number_key" in str(error.orig):
                #     duplicate_field = "phone_number"
                # print(str(error.orig))

            # Customize the response message based on the duplicate field
            raise GlobalException(
                StudentDuplicate(duplicate_fields=duplicate_fields),
                status.HTTP_400_BAD_REQUEST,
            )


# Not complete
@router.post("/forgot-password", response_model=ResetedSuccessful)
async def forget_password(data: ForgotPasswordData, maker: SessionMaker):
    try:
        async with maker.begin() as session:
            result = await session.execute(
                sa.select(Student).where(Student.email == data.email)
            )
            user = result.scalar()
            if user is None:
                raise GlobalException(InvalidEmail(), status.HTTP_400_BAD_REQUEST)

            reset_token = await to_async(create_reset_password_token, data.email)

            reset_link = f"https://{config.FRONTEND_DOMAIN}/{config.FORGOT_PASSWORD_URL}/{reset_token}"
            html = f"<a href='{reset_link}'>Click here to reset password</a>"

            message = MessageSchema(
                subject="Reset password instructions",
                recipients=[user.email],
                body=html,
                subtype=MessageType.html,
            )

            fm = FastMail(mail_conf)
            await fm.send_message(message)
            return ResetedSuccessful(message="Email has been sent")
    except Exception as ex:
        if isinstance(ex, GlobalException):
            raise
        raise GlobalException(UnknownError(), status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post(
    "/reset-password",
    response_model=ResetPasswordOut,
    responses={400: {"model": Union[InvalidResetLink, PasswordsDoseNotMatch]}},
)
async def reset_password(data: ResetForegetPasswordData, maker: SessionMaker):
    if data.secret_token is None or not data.secret_token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token.",
        )

    email = await to_async(decode_reset_password_token, data.secret_token)

    if email is None:
        raise GlobalException(InvalidResetLink(), status.HTTP_400_BAD_REQUEST)

    if not data.new_password.strip() or not data.confirm_password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fill the passsword fields.",
        )

    if data.new_password != data.confirm_password:
        raise GlobalException(PasswordsDoseNotMatch(), status.HTTP_400_BAD_REQUEST)

    hashed_password = await to_async(hash_password, data.new_password)

    async with maker.begin() as session:
        await session.execute(
            sa.update(Student)
            .where(Student.email == email)
            .values({"password": hashed_password})
        )

    return ResetPasswordOut()
