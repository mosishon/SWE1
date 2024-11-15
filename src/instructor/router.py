from fastapi import APIRouter, status
from sqlalchemy import insert

from src.authentication.dependencies import GetFullAdmin
from src.authentication.utils import hash_password, to_async
from src.dependencies import SessionMaker
from src.instructor.models import Instructor
from src.instructor.schemas import AddInstructorIn, InstructorCreated
from src.models import User
from src.schemas import UserFullInfo, UserRole

router = APIRouter(tags=["Instructor"])


@router.get("/test")
async def test():
    return


# TODO error handeling
@router.put(
    "/new-instructor",
    status_code=status.HTTP_201_CREATED,
    tags=["ByAdmin"],
    responses={201: {"model": InstructorCreated}},
)
async def new_instructor(data: AddInstructorIn, maker: SessionMaker, _: GetFullAdmin):
    async with maker.begin() as session:
        insert_query = (
            insert(User)
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
                    "role": UserRole.INSTRUCTOR,
                }
            )
            .returning(User)
        )
        try:
            insert_res = (await session.execute(insert_query)).scalar()
            if insert_res is not None:
                insert_ins_query = (
                    insert(Instructor)
                    .values({"for_user": insert_res.id})
                    .returning(Instructor.id)
                )
                insert_ins_res = (await session.execute(insert_ins_query)).scalar()
                if insert_ins_res is not None:
                    return InstructorCreated(
                        instuctor_id=insert_ins_res,
                        user_data=UserFullInfo.model_validate(insert_res),
                    )
        except Exception as ex:
            print(ex)
            raise
