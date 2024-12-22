from functools import lru_cache

import sqlalchemy as sa

from src.course.exceptions import SectionNotFound
from src.course.models import CourseSection, CourseSectionToInstructorAssociation
from src.database import get_session_maker
from src.dependencies import AsyncSession, async_sessionmaker
from src.exceptions import GlobalException
from src.instructor.exceptions import InstructorNotFound, SectionAlreadyEnrolled
from src.instructor.models import Instructor


class InstructorService:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker

    async def is_entity_exists(
        self, session: AsyncSession, model: sa.Table, entity_id: int
    ) -> bool:
        query = sa.select(sa.exists().where(model.c.id == entity_id))
        return (await session.execute(query)).scalar() or False

    async def is_instructor_exists(
        self, session: AsyncSession, instructor_id: int
    ) -> bool:
        is_instructor_exists = (
            await session.execute(
                sa.select(sa.exists().where(Instructor.id == instructor_id))
            )
        ).scalar() or False

        return bool(is_instructor_exists)

    async def get_instructor_by_id(
        self, session: AsyncSession, instructor_id: int
    ) -> Instructor | None:
        instructor = (
            await session.execute(
                sa.select(Instructor).filter(Instructor.id == instructor_id)
            )
        ).scalar()
        return instructor

    async def submit_section_enrollment(self, instructor_id: int):
        async with self.session_maker.begin() as session:
            instructor = await self.get_instructor_by_id(session, instructor_id)

            if instructor is None:
                raise GlobalException(InstructorNotFound(), 400)
            instructor.is_enrollment_submited = True
            session.add(instructor)
            await session.refresh(instructor)

    async def enroll_section(self, instructor_id: int, course_section_id: int):
        async with self.session_maker.begin() as session:
            # Check if instructor exists
            is_instructor_exists = await self.is_instructor_exists(
                session, instructor_id
            )
            if not is_instructor_exists:
                raise GlobalException(InstructorNotFound(), 400)

            # Check if Course section exists
            is_section_exists = (
                await session.execute(
                    sa.select(sa.exists().where(CourseSection.id == course_section_id))
                )
            ).scalar() or False
            if not is_section_exists:
                raise GlobalException(SectionNotFound(), 400)

            # Check if section already enrolled
            is_section_enrolled = (
                await session.execute(
                    sa.select(sa.func.count())
                    .select_from(CourseSectionToInstructorAssociation)
                    .filter(
                        CourseSectionToInstructorAssociation.course_section_id
                        == course_section_id
                    )
                    .filter(
                        CourseSectionToInstructorAssociation.instructor_id
                        == instructor_id
                    )
                )
            ).scalar() or 0

            if is_section_enrolled == 1:
                raise GlobalException(SectionAlreadyEnrolled(), 400)

            # Enroll section for instructor
            enroll_query = sa.insert(CourseSectionToInstructorAssociation).values(
                {"course_section_id": course_section_id, "instructor_id": instructor_id}
            )

            await session.execute(enroll_query)


@lru_cache()
def get_instructor_service() -> InstructorService:
    return InstructorService(get_session_maker())
