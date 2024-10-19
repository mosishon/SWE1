import sqlalchemy as sa
from fastapi import APIRouter

from src.authentication.dependencies import GetFullAdmin
from src.authentication.utils import hash_password, to_async
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
from src.student.models import Student
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
