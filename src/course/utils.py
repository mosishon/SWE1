import sqlalchemy as sa
from sqlalchemy.orm import selectinload

from src.database import get_session_maker
from src.instructor.models import Instructor


async def retreive_orginzer_data_from_db():
    maker = get_session_maker()
    async with maker.begin() as session:
        result = await session.execute(
            sa.select(Instructor)
            .options(selectinload(Instructor.available_times))
            .options(selectinload(Instructor.assigned_courses))
        )
        for inst in result.scalars().all():
            print(inst, inst.available_times, inst.assigned_courses)
