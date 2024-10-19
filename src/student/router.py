import sqlalchemy as sa
from fastapi import APIRouter

from src.authentication.dependencies import GetFullAdmin
from src.authentication.utils import hash_password, to_async
from src.database import get_session_maker
from src.models import User
from src.schemas import AddCode, AddMessage, UserFullInfo, UserRole
from src.student.models import Student
from src.student.schemas import StudentAdded, StudentInfo, StudentRegisterData

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
