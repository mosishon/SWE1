import sqlalchemy as sa
from fastapi import APIRouter, Query, status
from sqlalchemy.exc import IntegrityError

from src.authentication.dependencies import GetFullAdmin
from src.authentication.utils import hash_password, to_async
from src.course.exceptions import CourseNotFound
from src.course.models import Course
from src.course.schemas import (
    AddCourseOut,
    CourseSchema,
    ReserveCourseIn,
    UnReservedCourseIn,
    UnreservedCourseOut,
)
from src.database import get_session_maker
from src.dependencies import SessionMaker
from src.exceptions import GlobalException
from src.student.dependencies import GetFullStudent
from src.student.exceptions import StudentDuplicate, StudentNotFound
from src.student.models import ReservedCourse, Student
from src.student.schemas import (
    AllStudentsOut,
    StudentAdded,
    StudentDeleted,
    StudentDeleteIn,
    StudentRegisterData,
    StudentSchema,
)

router = APIRouter(prefix="/student", tags=["Student"])


@router.post("/new-student", response_model=StudentAdded, tags=["ByAdmin"])
async def create_new_student(
    register_data: StudentRegisterData, maker: SessionMaker, _: GetFullAdmin
):
    async with maker.begin() as session:
        try:
            student = await session.execute(
                sa.insert(Student)
                .values(
                    {
                        "id": register_data.student_id,
                        "first_name": register_data.first_name,
                        "last_name": register_data.last_name,
                        "national_id": register_data.national_id,
                        "email": register_data.email,
                        "username": register_data.student_id,
                        "phone_number": register_data.phone_number,
                        "birth_day": register_data.birth_day,
                        "password": await to_async(
                            hash_password, register_data.national_id
                        ),
                    }
                )
                .returning(Student)
            )
        except IntegrityError as error:
            duplicate_fields = []
            if "unique constraint" in str(error.orig):
                s = str(error.orig).find("(") + 1
                e = str(error.orig).find(")")
                duplicate_fields = [i.strip() for i in str(error.orig)[s:e].split(",")]

                # # Check for a specific constraint name or field in the error message
                # if "user_email_key" in str(error.orig):
                #     duplicate_field = "email"
                # elif "user_username_key" in str(error.orig):
                #     duplicate_field = "username"
                # elif "user_phone_number_key" in str(error.orig):
                #     duplicate_field = "phone_number"
                # print(str(error.orig))

            # Customize the response message based on the duplicate field
            raise GlobalException(
                StudentDuplicate(duplicate_fields=duplicate_fields),
                status.HTTP_400_BAD_REQUEST,
            )

        student = student.scalar()
        if student:
            return StudentAdded(student=StudentSchema.model_validate(student))


@router.post("/delete-student")
async def delete_student(
    data: StudentDeleteIn, maker: SessionMaker, _: GetFullAdmin
) -> StudentDeleted:
    async with maker.begin() as session:
        stu = await session.execute(
            sa.select(sa.func.count(Student.id)).where(Student.id == data.student_id)
        )
        stu = stu.scalar()
        if stu is not None:
            await session.execute(
                sa.delete(Student).where(Student.id == data.student_id)
            )
            return StudentDeleted(
                student=StudentSchema.model_validate(stu),
            )
        else:
            raise GlobalException(StudentNotFound(), status.HTTP_400_BAD_REQUEST)


@router.post(
    "/reserve-course",
    response_model=AddCourseOut,
    responses={404: {"model": CourseNotFound}},
)
async def reserve_course(
    data: ReserveCourseIn, student: GetFullStudent
) -> AddCourseOut:
    async with get_session_maker().begin() as session:
        student_id = student.id
        check_result = await session.execute(
            sa.select(Course).where(Course.id == data.course_id)
        )
        course = check_result.scalar()
        if course is None:
            raise GlobalException(CourseNotFound(), 400)
        query = sa.insert(ReservedCourse).values(
            {
                ReservedCourse.course_id: data.course_id,
                ReservedCourse.student_id: student_id,
            }
        )
        await session.execute(query)
        return AddCourseOut(course=CourseSchema.model_validate(course))


@router.delete(
    "/unreserve-course",
    response_model=UnreservedCourseOut,
    responses={404: {"model": CourseNotFound}},
)
async def unreserve_course(
    data: UnReservedCourseIn, student: GetFullStudent, maker: SessionMaker
) -> UnreservedCourseOut:
    async with maker.begin() as session:
        check_result = await session.execute(
            sa.select(Course).where(Course.id == data.course_id)
        )

        course = check_result.scalar()
        if not course:
            raise GlobalException(CourseNotFound(), 400)

        query = (
            sa.delete(ReservedCourse)
            .where(ReservedCourse.student_id == student.id)
            .where(ReservedCourse.course_id == data.course_id)
        )

        await session.execute(query)

        return UnreservedCourseOut(course=CourseSchema.model_validate(course))


@router.get(
    "/reserved-course",
)
async def get_reserved_course(student: GetFullStudent):
    async with get_session_maker().begin() as session:
        student_id = student.id
        query = (
            sa.select(Course.name, Course.unit)
            .join(ReservedCourse)
            .where(ReservedCourse.student_id == student_id)
        )
        result = await session.execute(query)
        _ = result.scalars().all()
        # Todo need check response
        raise GlobalException(
            StudentNotFound(), status_code=status.HTTP_400_BAD_REQUEST
        )


@router.get("/all")
async def get_all_students(
    _: GetFullAdmin,
    maker: SessionMaker,
    limit: int = Query(gt=0, default=10, lt=25),
    offset: int = Query(gt=-1, default=0),
) -> AllStudentsOut:
    async with maker.begin() as session:
        query = sa.select(Student).limit(limit=limit).offset(offset=offset)

        res = await session.execute(query)

        students = [StudentSchema.model_validate(student) for student in res]

        return AllStudentsOut(students=students, count=len(students))
