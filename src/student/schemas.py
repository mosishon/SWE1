from pydantic import BaseModel

from src.cutsom_types import StudnentID
from src.schemas import ObjectAdded, ObjectDeleted, UserFullInfo, UserRegisterData


class StudentRegisterData(UserRegisterData):
    student_id: StudnentID


class StudentDeleteIn(BaseModel):
    student_id: StudnentID


class FullStudent(BaseModel):
    user: UserFullInfo
    student_id: StudnentID


class StudentInfo(BaseModel):
    user: UserFullInfo
    student_id: StudnentID

    class Config:
        from_attributes = True


class StudentAdded(ObjectAdded):
    student: StudentInfo


class StudentDeleted(ObjectDeleted):
    student: StudentInfo
