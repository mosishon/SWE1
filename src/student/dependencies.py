from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, HTTPException, status

from src.authentication.dependencies import GetFullUser
from src.dependencies import SessionMaker
from src.student.models import Student
from src.student.schemas import FullStudent


async def get_student(maker: SessionMaker, full_user: GetFullUser) -> FullStudent:
    async with maker.begin() as session:
        result = await session.execute(
            sa.select(Student.student_id).where(Student.for_user == full_user.id)
        )
        student_id = result.scalar_one_or_none()
        if student_id is not None:
            return FullStudent(full_user=full_user, student_id=student_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not student",
                headers={"WWW-Authenticate": "Bearer"},
            )


GetFullStudent = Annotated[FullStudent, Depends(get_student)]
