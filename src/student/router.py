import sqlalchemy as sa
from fastapi import APIRouter

from src.authentication.dependencies import GetFullAdmin
from src.authentication.utils import hash_password, to_async
from src.course.models import Course
from src.course.schemas import AddCourseIn, AddCourseOut
from src.database import get_session_maker
from src.exceptions import GlobalException
from src.models import User
from src.schemas import UserFullInfo, UserRole
from src.student.dependencies import GetFullStudent
from src.student.exceptions import CourseNotFound
from src.student.models import Student, StudentCourse
from src.student.schemas import (
    StudentAdded,
    StudentDeleted,
    StudentDeleteIn,
    StudentInfo,
    StudentNotFound,
    StudentRegisterData,
)

router = APIRouter()


@router.post("/new-student", response_model=StudentAdded)
async def create_new_student(register_data: StudentRegisterData, _: GetFullAdmin):
    async with get_session_maker().begin() as session:
        user = await session.execute(
            sa.insert(User)
            .values(
                {
                    "first_name": register_data.first_name,
                    "last_name": register_data.last_name,
                    "national_id": register_data.national_id,
                    "email": register_data.email,
                    "username": register_data.student_id,
                    "phone_number": register_data.phone_number,
                    "birth_day": register_data.birth_day,
                    "password": await to_async(
                        hash_password(register_data.national_id)
                    ),
                    "role": UserRole.STUDENT,
                }
            )
            .returning(User.id)
        )
        user = user.first()
        if user:
            uid = user[0]
            await session.execute(
                sa.insert(Student).values(
                    {"student_id": register_data.student_id, "for_user": uid}
                )
            )
            await session.commit()
            fu = UserFullInfo(
                first_name=register_data.first_name,
                last_name=register_data.last_name,
                birth_day=register_data.birth_day,
                email=register_data.email,
                national_id=register_data.national_id,
                phone_number=register_data.phone_number,
            )
            return StudentAdded(
                student=StudentInfo(user=fu, student_id=register_data.student_id),
            )


@router.post("/delete-student", response_model=StudentAdded)
async def delete_student(data: StudentDeleteIn, _: GetFullAdmin):
    async with get_session_maker().begin() as session:
        stu = await session.execute(
            sa.select(Student.for_user).where(Student.student_id == data.student_id)
        )
        stu = stu.scalar_one_or_none()
        if stu:
            user = await session.execute(sa.select(User).where(User.id == stu))
            user = user.scalar_one_or_none()
            if not user:
                return {}  # TODO return error
            await session.execute(
                sa.delete(Student).where(Student.student_id == data.student_id)
            )
            await session.execute(sa.delete(User).where(User.id == stu))
            fu = UserFullInfo.model_validate(user)
            return StudentDeleted(
                student=StudentInfo(user=fu, student_id=data.student_id),
            )
        else:
            return {}  # TODO return error


@router.post(
    "/reserve-course",
    response_model=AddCourseOut,
    responses={404: {"model": CourseNotFound}},
)
async def reserve_course(data: AddCourseIn, student: GetFullStudent):
    async with get_session_maker().begin() as session:
        student_id = student.student_id
        check_result = await session.execute(
            sa.select(Course).where(Course.id == data.course_id)
        )
        course = check_result.scalar_one_or_none()
        if not course:
            raise GlobalException(CourseNotFound(), 400)
        query = sa.insert(StudentCourse).values(
            {
                StudentCourse.course_id: data.course_id,
                StudentCourse.student_id: student_id,
            }
        )
        await session.execute(query)
        return AddCourseOut(course_name=course.name)


@router.get(
    "/reserved-course",
)
async def get_reserved_course(student: GetFullStudent):
    async with get_session_maker().begin() as session:
        student_id = student.student_id
        query = (
            sa.select(Course.name, Course.unit)
            .join(StudentCourse)
            .where(StudentCourse.student_id == student_id)
        )
        result = await session.execute(query)
        _ = result.scalars().all()
        # Todo need check response
        return StudentNotFound(details="Student not found"), 404
