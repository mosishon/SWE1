from pydantic import BaseModel

from src.cutsom_types import StudnentID
from src.schemas import FullUser, UserInfoL1, UserRegisterData


class StudentRegisterData(UserRegisterData):
    student_id: StudnentID


class FullStudent(BaseModel):
    full_user: FullUser
    student_id: StudnentID


class StudentInfo(UserInfoL1):
    student_id: StudnentID
