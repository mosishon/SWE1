from fastapi import APIRouter, status
from sqlalchemy import func, insert, select

from src.authentication.dependencies import GetFullAdmin
from src.course.exceptions import CourseExists, SectionExists
from src.course.models import Course, CourseSection, CourseSectionToCourseAssociation
from src.course.schemas import (
    AddCourseIn,
    AddSectionIn,
    AllCoursesCourse,
    AllCoursesInstructor,
    AllCoursesOut,
    CourseCreated,
)
from src.course.schemas import CourseSection as PydanticCourseSeciton
from src.course.schemas import SectionCreated
from src.dependencies import SessionMaker
from src.exceptions import GlobalException
from src.instructor.models import Instructor
from src.models import User
from src.schemas import FullUser

router = APIRouter(prefix="/course", tags=["Courses"])


@router.put(
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


# TODO Error Handeling
@router.get(
    "/all", status_code=status.HTTP_200_OK, responses={200: {"model": AllCoursesOut}}
)
async def get_all_courses(
    maker: SessionMaker, _: GetFullAdmin, limit: int = 10, offset: int = 0
):
    async with maker.begin() as session:
        query = (
            select(Course, Instructor, User, CourseSection)
            .join(
                Instructor, Course.instructor_id == Instructor.id
            )  # Join with Instructor
            .join(
                User,
                Instructor.for_user == User.id,
            )  # Join with User
            .join(
                CourseSectionToCourseAssociation,
                Course.id == CourseSectionToCourseAssociation.c.course_id,
            )  # Join association table
            .join(
                CourseSection,
                CourseSection.id
                == CourseSectionToCourseAssociation.c.course_section_id,
            )  # Join with CourseSection
            .limit(limit)
            .offset(offset)
        )

        course = await session.execute(query)

        result_dict = {}

        # Iterate over the raw query results
        courses = []
        for row in course.all():
            course, instructor, user, section = row.tuple()
            # course_id = course.id  # Assuming `id` is a unique identifier for the course
            if course not in result_dict:
                result_dict[course] = {
                    "course": course,
                    "instructor": {"inst": instructor, "user": user},
                    "sections": [],
                }
            result_dict[course]["sections"].append(section)
        for c in result_dict:
            sections = result_dict[c]["sections"]
            instructor = result_dict[c]["instructor"]
            sections_obj = [
                PydanticCourseSeciton.model_validate(sec) for sec in sections
            ]
            courses.append(
                AllCoursesCourse(
                    name=c.name,
                    short_name=c.short_name,
                    sections_count=c.sections_count,
                    unit=c.unit,
                    importance=c.importance,
                    sections=sections_obj,
                    instructor=AllCoursesInstructor(
                        full_user=FullUser.model_validate(user),
                        instructor_id=instructor["inst"].id,
                    ),
                )
            )
        return AllCoursesOut(courses=courses, count=len(courses))


@router.put(
    "/new-course",
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": CourseExists}, 201: {"model": SectionCreated}},
    tags=["ByAdmin"],
)
async def new_course(data: AddCourseIn, maker: SessionMaker, _: GetFullAdmin):
    async with maker.begin() as session:
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
                    "instructor_id": data.instructor_id,
                    "sections_count": data.section_count,
                    "unit": data.unit,
                    "importance": data.importance,
                }
            )
            .returning(Course.id)
        )

        insert_res = (await session.execute(insert_query)).scalar()
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
