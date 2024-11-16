import datetime
from typing import Annotated

import jwt
import pydantic
import sqlalchemy as sa
from fastapi import Depends, HTTPException, status

from src import config
from src.authentication.constants import ALGORITHM
from src.authentication.dependencies import BackendToken
from src.authentication.schemas import TokenData
from src.dependencies import SessionMaker
from src.schemas import UserRole
from src.student.models import Student
from src.student.schemas import StudentSchema


async def get_current_student(
    maker: SessionMaker, token: BackendToken
) -> StudentSchema:
    try:
        algs = [ALGORITHM]
        payload = jwt.decode(token, config.config.SECRET, algorithms=algs)
        token_data = TokenData(**payload)
        if token_data.role != UserRole.STUDENT:
            raise pydantic.ValidationError()
        if datetime.datetime.fromtimestamp(token_data.exp) < datetime.datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.InvalidTokenError, pydantic.ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    async with maker.begin() as session:
        result = await session.execute(
            sa.select(Student).where(Student.id == token_data.user_id)
        )
        user = result.scalar()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find user",
            )

        return StudentSchema.model_validate(user)


GetFullStudent = Annotated[StudentSchema, Depends(get_current_student)]
