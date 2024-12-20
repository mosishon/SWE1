from functools import lru_cache

import sqlalchemy as sa

from src.course.models import CourseSection
from src.database import AsyncSession, async_sessionmaker, get_session_maker


class SectionService:
    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
    ):
        self.session_maker = session_maker

    async def is_section_exists(self, session: AsyncSession, section_id: int) -> bool:
        is_instructor_exists = (
            await session.execute(
                sa.select(sa.exists().where(CourseSection.id == section_id))
            )
        ).scalar() or False

        return bool(is_instructor_exists)

    async def get_section_by_id(
        self, session: AsyncSession, section_id: int
    ) -> CourseSection | None:
        section = (
            await session.execute(
                sa.select(CourseSection).filter(CourseSection.id == section_id)
            )
        ).scalar()
        return section


@lru_cache()
def get_section_service() -> SectionService:
    return SectionService(get_session_maker())
