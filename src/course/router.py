from fastapi import APIRouter, Query, status
from sqlalchemy import delete, func, insert, select

from src.authentication.dependencies import GetFullAdmin
from src.course.exceptions import (
    CourseExists,
    CourseNotFound,
    SectionExists,
    SectionNotFound,
)
from src.course.models import (
    Course,
    CourseSection,
    CourseSectionToCourseAssociation,
    CourseSectionToInstructorAssociation,
)
from src.course.schemas import (
    AddCourseIn,
    AddSectionIn,
    AllCoursesOut,
    CourseCreated,
    CourseDeleted,
    CourseSchema,
    CourseSectionSchema,
    DeleteCourse,
    DeleteSectionIn,
    ListSections,
    SectionCreated,
    SectionDeleted,
)
from src.dependencies import SessionMaker
from src.exceptions import GlobalException, UnknownError
from src.instructor.exceptions import InstructorNotFound
from src.instructor.models import CourseInstructor, Instructor
from src.instructor.schemas import InstructorSchema

router = APIRouter(prefix="/course", tags=["Courses"])


@router.post(
    "/new-section",
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": SectionExists}, 201: {"model": SectionCreated}},
    tags=["ByAdmin"],
)
async def new_section(data: AddSectionIn, maker: SessionMaker, _: GetFullAdmin):
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


@router.delete(
    "/delete-section",
    status_code=status.HTTP_200_OK,
    tags=["ByAdmin"],
    responses={400: {"model": SectionNotFound}},
)
async def delete_section(_: GetFullAdmin, maker: SessionMaker, data: DeleteSectionIn):
    async with maker.begin() as session:
        section = await session.execute(
            select(CourseSection).where(CourseSection.id == data.section_id)
        )

        check_section = section.scalar()

        if check_section is None:
            raise GlobalException(SectionNotFound(), status.HTTP_400_BAD_REQUEST)

        query1 = delete(CourseSectionToCourseAssociation).where(
            CourseSectionToCourseAssociation.course_section_id == data.section_id
        )
        query2 = delete(CourseSectionToInstructorAssociation).where(
            CourseSectionToInstructorAssociation.course_section_id == data.section_id
        )
        query = delete(CourseSection).where(CourseSection.id == data.section_id)

        await session.execute(query1)
        await session.execute(query2)
        await session.execute(query)

        return SectionDeleted(section=CourseSectionSchema.model_validate(check_section))


# TODO Error Handeling
@router.get(
    "/all", status_code=status.HTTP_200_OK, responses={200: {"model": AllCoursesOut}}
)
async def get_all_courses(
    maker: SessionMaker,
    _: GetFullAdmin,
    limit: int = Query(gt=0, default=10, lt=25),
    offset: int = Query(gt=-1, default=0),
):
    async with maker.begin() as session:
        query = (
            select(Course, Instructor, CourseSection)
            .select_from(Course)
            .join(CourseInstructor, CourseInstructor.course_id == Course.id)
            .join(
                Instructor, CourseInstructor.instructor_id == Instructor.id
            )  # Join with Instructor
            .join(
                CourseSectionToCourseAssociation,
                Course.id == CourseSectionToCourseAssociation.course_id,
            )  # Join association table
            .join(
                CourseSection,
                CourseSection.id == CourseSectionToCourseAssociation.course_section_id,
            )  # Join with CourseSection
            .limit(limit)
            .offset(offset)
        )

        course = await session.execute(query)
        result_dict = {}

        # Iterate over the raw query results
        courses = []
        for row in course.all():
            course, instructor, section = row.tuple()
            # course_id = course.id  # Assuming `id` is a unique identifier for the course
            if course not in result_dict:
                result_dict[course] = {
                    "course": course,
                    "instructor": instructor,
                    "sections": [],
                }
            result_dict[course]["sections"].append(section)
        for c in result_dict:
            sections = result_dict[c]["sections"]
            instructor = result_dict[c]["instructor"]
            sections_obj = [CourseSectionSchema.model_validate(sec) for sec in sections]
            courses.append(
                CourseSchema(
                    id=c.id,
                    name=c.name,
                    short_name=c.short_name,
                    sections_count=c.sections_count,
                    unit=c.unit,
                    importance=c.importance,
                    sections=sections_obj,
                    instructor=InstructorSchema.model_validate(instructor),
                )
            )
        return AllCoursesOut(courses=courses, count=len(courses))


@router.get("/all-sections")
async def all_sections(maker: SessionMaker, _: GetFullAdmin) -> ListSections:
    async with maker.begin() as session:
        sections = (await session.execute(select(CourseSection))).scalars().all()
        objs = [CourseSectionSchema.model_validate(sec) for sec in sections]
        return ListSections(sections=objs, count=len(objs))


@router.post(
    "/new-course",
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": CourseExists | InstructorNotFound}},
    tags=["ByAdmin"],
)
async def new_course(
    data: AddCourseIn, maker: SessionMaker, _: GetFullAdmin
) -> CourseCreated:
    async with maker.begin() as session:
        check_sections_query = (
            select(func.count())
            .select_from(CourseSection)
            .filter(CourseSection.id.in_(data.sections_id))
        )
        check_sections_res = (await session.execute(check_sections_query)).scalar()
        if check_sections_res is not None and check_sections_res != len(
            data.sections_id
        ):
            raise GlobalException(SectionNotFound(), status.HTTP_400_BAD_REQUEST)
        check_inst_query = select(Instructor).filter(
            Instructor.id == data.instructor_id
        )
        check_inst_res = (await session.execute(check_inst_query)).scalar()
        if check_inst_res is None:
            raise GlobalException(InstructorNotFound(), status.HTTP_400_BAD_REQUEST)
        query = (
            select(func.count(Course.id))
            .select_from(Course)
            .filter(Course.name == data.name)
            .filter(Course.short_name == data.short_name)
            .filter(Course.group == data.group)
        )
        res = await session.execute(query)
        c = res.scalar()
        if c is not None and c > 0:
            raise GlobalException(CourseExists(), 400)
        insert_query = (
            insert(Course)
            .values(
                {
                    "name": data.name,
                    "short_name": data.short_name,
                    "group": data.group,
                    "sections_count": data.section_count,
                    "unit": data.unit,
                    "importance": data.importance,
                }
            )
            .returning(Course.id)
        )

        course_id = insert_res = (await session.execute(insert_query)).scalar()
        insert_course_instructor_query = insert(CourseInstructor).values(
            {"instructor_id": data.instructor_id, "course_id": course_id}
        )
        await session.execute(insert_course_instructor_query)

        if insert_res is not None:
            sections = [
                {"course_id": insert_res, "course_section_id": section_id}
                for section_id in data.sections_id
            ]
            insert_section_query = insert(CourseSectionToCourseAssociation).values(
                sections
            )
            await session.execute(insert_section_query)

            return CourseCreated(course_id=insert_res)
        else:
            raise GlobalException(UnknownError(), status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete(
    "/delete-course",
    responses={400: {"model": CourseNotFound}},
)
async def delete_course(
    _: GetFullAdmin, maker: SessionMaker, data: DeleteCourse
) -> CourseDeleted:
    async with maker.begin() as session:
        check_course = (
            await session.execute(select(Course).where(Course.id == data.course_id))
        ).scalar()

        if check_course is None:
            raise GlobalException(CourseNotFound(), status.HTTP_400_BAD_REQUEST)
        query = delete(Course).where(Course.id == data.course_id)

        await session.execute(query)

        return CourseDeleted(course=CourseSchema.model_validate(check_course))
