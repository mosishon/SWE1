from fastapi import APIRouter
from sqlalchemy import func, insert, select

from src.authentication.dependencies import GetFullAdmin
from src.course.exceptions import SectionExists
from src.course.models import CourseSection
from src.course.schemas import AddSectionIn, SectionCreated
from src.dependencies import SessionMaker
from src.exceptions import GlobalException

router = APIRouter(prefix="/course", tags=["Courses"])


@router.put("/new-section", responses={400: {"model": SectionExists}})
async def new_course(data: AddSectionIn, maker: SessionMaker, _: GetFullAdmin):
    async with maker.begin() as session:
        query = (
            select(func.count(CourseSection.id))
            .select_from(CourseSection)
            .filter(CourseSection.day_of_week == data.week_day)
            .filter(CourseSection.start_time == data.start_time)
            .filter(CourseSection.end_time == data.end_time)
        )
        res = await session.execute(query)
        c = res.scalar()
        if c is not None and c > 0:
            raise GlobalException(SectionExists(), 400)
        insert_query = (
            insert(CourseSection)
            .values(
                {
                    "day_of_week": data.week_day,
                    "start_time": data.start_time,
                    "end_time": data.end_time,
                }
            )
            .returning(CourseSection.id)
        )
        insert_res = (await session.execute(insert_query)).scalar()
        if insert_res is not None:
            return SectionCreated(section_id=insert_res)
