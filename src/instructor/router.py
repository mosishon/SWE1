from fastapi import APIRouter, status, HTTPException
from sqlalchemy import insert, select, delete

from src.authentication.dependencies import GetFullAdmin
from src.authentication.utils import hash_password, to_async
from src.course.models import CourseSection, CourseSectionToInstructorAssociation
from src.course.schemas import CourseSectionSchema
from src.dependencies import SessionMaker
from src.instructor.models import Instructor
from src.instructor.schemas import AddInstructorIn, InstructorCreated, InstructorSchema, DeleteInstructorIn

router = APIRouter(tags=["Instructor"])


@router.get("/test")
async def test():
    return


# TODO error handeling
@router.post(
    "/new-instructor",
    status_code=status.HTTP_201_CREATED,
    tags=["ByAdmin"],
    responses={201: {"model": InstructorCreated}},
)
async def new_instructor(data: AddInstructorIn, maker: SessionMaker, _: GetFullAdmin):
    async with maker.begin() as session:
        try:
            insert_ins_query = (
                insert(Instructor)
                .values(
                    {
                        "first_name": data.first_name,
                        "last_name": data.last_name,
                        "national_id": data.national_id,
                        "email": data.email,
                        "username": data.email,
                        "phone_number": data.phone_number,
                        "birth_day": data.birth_day,
                        "password": await to_async(hash_password, data.national_id),
                    }
                )
                .returning(Instructor)
            )
            insert_ins_res = (await session.execute(insert_ins_query)).scalar()
            sections = []
            if insert_ins_res is not None:
                if (
                    data.available_sections is not None
                    and len(data.available_sections) > 0
                ):
                    insert_sections_query = insert(
                        CourseSectionToInstructorAssociation
                    ).values(
                        [
                            {
                                "instructor_id": insert_ins_res.id,
                                "course_section_id": csid,
                            }
                            for csid in data.available_sections
                        ]
                    )
                    await session.execute(insert_sections_query)
                    sections = (
                        await session.execute(
                            select(CourseSection).filter(
                                CourseSection.id.in_(data.available_sections)
                            )
                        )
                    ).scalars()

                inst_obj = InstructorSchema.model_validate(insert_ins_res)
                inst_obj.available_sections = [
                    CourseSectionSchema.model_validate(item) for item in sections
                ]
                return InstructorCreated(instuctor=inst_obj)
        except Exception as ex:
            print(ex)
            raise



@router.delete(
    "/delete-instructor",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["ByAdmin"]
)
async def delete_instructor(_: GetFullAdmin, maker: SessionMaker, data: DeleteInstructorIn):
    async with maker().begin() as session:
        
        check_instructor = await session.execute(
             select(Instructor)
            .where(Instructor.id == data.instructor_id)
        )

        instructor = check_instructor.scalar_one_or_none()
        if not instructor:
            raise HTTPException(status_code=404, detail=f'Instructor is not found')        

        query = (
            delete(Instructor)
            .where(Instructor.id == data.instructor_id)
        )

        await session.execute(query)

