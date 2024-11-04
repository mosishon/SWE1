from typing import Literal

from pydantic import BaseModel

from src.cutsom_types import StudnentID
from src.schemas import (
    ErrorCode,
    FullUser,
    ObjectAdded,
    ObjectDeleted,
    UserFullInfo,
    UserRegisterData,
)


class StudentRegisterData(UserRegisterData):
    student_id: StudnentID


class StudentDeleteIn(BaseModel):
    student_id: StudnentID


class FullStudent(BaseModel):
    full_user: FullUser
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


class StudentNotFound(BaseModel):
    code: Literal[ErrorCode.STUDENT_NOT_FOUND] = ErrorCode.STUDENT_NOT_FOUND
    details: str


class StudentDuplicate(BaseModel):
    code: ErrorCode = ErrorCode.STUDENT_DUPLICATE
    details: str
