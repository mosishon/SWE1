import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr

from src.cutsom_types import StudnentID
from src.schemas import (
    Messages,
    ObjectAdded,
    ObjectDeleted,
    SuccessCodes,
    UserFullInfo,
    UserRegisterData,
)


class StudentRegisterData(UserRegisterData):
    student_id: StudnentID


class StudentDeleteIn(BaseModel):
    student_id: StudnentID


class StudentSchema(BaseModel):
    id: str
    first_name: str
    last_name: str
    national_id: str
    email: EmailStr
    username: str
    phone_number: str
    birth_day: datetime.date

    class Config:
        from_attributes = True


class StudentInfo(BaseModel):
    user: UserFullInfo
    student_id: StudnentID

    class Config:
        from_attributes = True


class StudentAdded(ObjectAdded):
    code: Literal[SuccessCodes.STUDENT_ADDED] = SuccessCodes.STUDENT_ADDED
    message: Literal[Messages.STUDENT_ADDED] = Messages.STUDENT_ADDED
    student: StudentSchema


class StudentDeleted(ObjectDeleted):
    code: Literal[SuccessCodes.STUDENT_DELETED] = SuccessCodes.STUDENT_DELETED
    message: Literal[Messages.STUDENT_DELETED] = Messages.STUDENT_DELETED
    student: StudentSchema


# class StudentNotFound(BaseModel):
#     code: Literal[ErrorCode.STUDENT_NOT_FOUND] = ErrorCode.STUDENT_NOT_FOUND
#     details: str


class AllStudentsOut(BaseModel):
    students: list[StudentSchema]
    count: int
