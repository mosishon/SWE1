import datetime

import jwt
import sqlalchemy as sa
from fastapi import HTTPException, status
from pydantic import ValidationError

from src.authentication.constants import ALGORITHM
from src.authentication.schemas import TokenData
from src.config import config
from src.course.schemas import CourseSection
from src.dependencies import BackendToken, GetFullUser, SessionMaker
from src.instructor.models import Instructor
from src.instructor.schemas import FullInstructor
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


async def get_instructor(maker: SessionMaker, full_user: GetFullUser) -> FullInstructor:
    async with maker.begin() as session:
        result = await session.execute(
            sa.select(Instructor).where(Instructor.for_user == full_user.id)
        )
        instructor = result.scalar_one_or_none()
        if instructor:
            course_sections = map(
                CourseSection.model_validate, instructor.available_course_sections
            )
            return FullInstructor(
                full_user=full_user, available_course_sections=list(course_sections)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return FullInstructor()
