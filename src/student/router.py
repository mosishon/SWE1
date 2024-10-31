import sqlalchemy as sa
from fastapi import APIRouter

from src.authentication.dependencies import GetFullAdmin, GetFullUser
from src.authentication.utils import hash_password, to_async
from src.course.models import Course
from src.course.schemas import AddCourseIn, AddCourseOut
from src.database import get_session_maker
from src.models import User
from src.schemas import (
    AddCode,
    AddMessage,
    DeleteCode,
    DeleteMessage,
    UserFullInfo,
    UserRole,
)
from src.student.models import Student, Student_Course
from src.student.schemas import (
    StudentAdded,
    StudentDeleted,
    StudentDeleteIn,
    StudentInfo,
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
                code=AddCode.STUDENT_ADDED,
                message=AddMessage.STUDENT_ADDED,
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
                code=DeleteCode.STUDENT_DELETED,
                message=DeleteMessage.STUDENT_DELETED,
                student=StudentInfo(user=fu, student_id=data.student_id),
            )
        else:
            return {}  # TODO return error


@router.post("/add-course", response_model=AddCourseOut)
async def add_course(data: AddCourseIn, user: GetFullUser):
    async with get_session_maker().begin() as session:
        student_id = await session.execute(
            sa.select(Student.student_id).where(Student.for_user == user.id)
        )
        query = sa.insert(Student_Course).values(
            {
                Student_Course.course_id: data.course_id,
                Student_Course.student_id: student_id,
            }
        )
        await session.execute(query)

    return AddCourseOut(course_name=data.course_name)


@router.get("/reserved-course")
async def get_reserved_course(user: GetFullUser):
    async with get_session_maker().begin() as session:
        student_id = await session.execute(
            sa.select(Student.student_id).where(Student.for_user == user.id)
        )
        query = (
            sa.select(Course.name, Course.unit)
            .join(Student_Course)
            .where(Student_Course.student_id == student_id)
        )
        result = await session.execute(query)

        return result
