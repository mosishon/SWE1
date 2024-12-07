from typing import Dict

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from src.authentication.dependencies import GetFullAdmin
from src.authentication.utils import hash_password, to_async
from src.course.models import CourseSection, CourseSectionToInstructorAssociation
from src.course.schemas import CourseSectionSchema
from src.dependencies import SessionMaker
from src.exceptions import GlobalException
from src.instructor.exceptions import InstructorNotFound
from src.instructor.models import Instructor
from src.instructor.schemas import (
    AddInstructorIn,
    DeleteInstructorIn,
    InstructorCreated,
    InstructorDeleted,
    InstructorListResponse,
    InstructorSchema,
    UpdateInstructorIn,
)

router = APIRouter(tags=["Instructor"])


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
            else:
                raise HTTPException(500, "error in adding")
        except Exception as ex:
            print(ex)
            raise


@router.delete(
    "/delete-instructor",
    tags=["ByAdmin"],
    responses={400: {"model": InstructorNotFound}},
)
async def delete_instructor(
    _: GetFullAdmin,
    maker: SessionMaker,
    data: DeleteInstructorIn,
) -> InstructorDeleted:
    async with maker.begin() as session:
        check_instructor = await session.execute(
            select(Instructor).where(Instructor.id == data.instructor_id)
        )

        instructor = check_instructor.scalar()
        if instructor is None:
            raise GlobalException(InstructorNotFound(), status.HTTP_400_BAD_REQUEST)

        query = delete(Instructor).where(Instructor.id == data.instructor_id)

        await session.execute(query)
        return InstructorDeleted(instructor=InstructorSchema.model_validate(instructor))


@router.get("/all", response_model=InstructorListResponse)
async def get_instructors(
    maker: SessionMaker,
    _: GetFullAdmin,
    limit: int = Query(
        10, ge=1, le=20, description="Maximum number of instructors to retrieve"
    ),
    offset: int = Query(0, ge=0, description="Number of instructors to skip"),
):
    try:
        async with maker.begin() as session:
            # Query to fetch instructors and their course sections
            query = (
                select(Instructor, CourseSection)
                .select_from(Instructor)
                .join(
                    CourseSectionToInstructorAssociation,
                    CourseSectionToInstructorAssociation.instructor_id == Instructor.id,
                    isouter=True,
                )
                .join(
                    CourseSection,
                    CourseSection.id
                    == CourseSectionToInstructorAssociation.course_section_id,
                    isouter=True,
                )
                .offset(offset)
                .limit(limit)
            )

            # Execute query
            instructors_query = await session.execute(query)
            instructors = instructors_query.tuples().all()
            print(instructors)
            # Build instructor to course section mapping
            maps: Dict[Instructor, list[CourseSection]] = {}
            for tup in instructors:
                inst, sec = tup
                print(inst.first_name, inst.id)
                if inst in maps.keys():
                    maps[inst].append(sec)
                else:
                    maps[inst] = [sec]

            # Validate and construct response
            inst_objects = []
            for inst in maps.keys():
                try:
                    schema = InstructorSchema.model_validate(inst)
                    schema.available_sections = [
                        CourseSectionSchema.model_validate(cs)
                        for cs in maps[inst]
                        if cs is not None
                    ]
                    inst_objects.append(schema)
                except ValidationError as ve:
                    raise HTTPException(
                        status_code=422, detail=f"Validation error: {ve.errors()}"
                    )

            return InstructorListResponse(
                instructors=inst_objects, total=len(inst_objects)
            )

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Validation error: {ve.errors()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.put("/update-instructor/{Instructor_id}")
async def update_instructor(
    _: GetFullAdmin, data: UpdateInstructorIn, maker: SessionMaker, Instructor_id
):
    async with maker.begin() as session:
        check_instructor = await session.execute(
            select(Instructor).where(Instructor.id == int(Instructor_id))
        )

        if not check_instructor.scalar():
            raise HTTPException(status_code=404, detail="Instructor is not found")

        UpdateData = data.dict(exclude_unset=True)

        if not UpdateData:
            raise HTTPException(
                status_code=400,
                detail="No fields or correct fields provided for update",
            )

        for val in UpdateData.values():
            if not val.strip():
                raise HTTPException(
                    status_code=400, detail="Fill the field with proper value"
                )

        query = (
            update(Instructor)
            .where(Instructor.id == int(Instructor_id))
            .values(**UpdateData)
        )

        await session.execute(query)

        return {
            "message": "Instructor updated successfully",
            "updated_fields": UpdateData,
        }
