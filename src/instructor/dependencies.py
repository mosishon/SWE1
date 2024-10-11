from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, HTTPException, status

from src.authentication.dependencies import GetFullUser
from src.course.schemas import CourseSection
from src.dependencies import SessionMaker
from src.instructor.models import Instructor
from src.instructor.schemas import FullInstructor


async def get_instructor(maker: SessionMaker, full_user: GetFullUser) -> FullInstructor:
    async with maker.begin() as session:
        print("d")
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
                detail="You are not instructor",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return FullInstructor()


GetFullInstructor = Annotated[FullInstructor, Depends(get_instructor)]
