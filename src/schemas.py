import enum

from pydantic import BaseModel, EmailStr, NaiveDatetime

from src.cutsom_types import HashedPassword, NationalID, PhoneNumber


class AddCode(enum.Enum):
    STUDENT_ADDED = "STUDENT_ADDED"


class DeleteCode(enum.Enum):
    STUDENT_DELETED = "STUDENT_DELETED"


class AddMessage(enum.Enum):
    STUDENT_ADDED = "Student added successfully"


class DeleteMessage(enum.Enum):
    STUDENT_DELETED = "Student deleted successfully"


class UserRole(enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"
    INSTRUCTOR = "instructor"


class ErrorCode(str, enum.Enum):
    COURSE_NOT_FOUND = "COURSE_NOT_FOUND"
    STUDENT_NOT_FOUND = "STUDENT_NOT_FOUND"
    STUDENT_DUPLICATE = "STUDENT_DUPLICATE"


class BaseUser(BaseModel):
    first_name: str
    last_name: str
    birth_day: NaiveDatetime


class UserFullInfo(BaseUser):
    email: EmailStr
    national_id: NationalID
    phone_number: PhoneNumber

    class Config:
        from_attributes = True


class UserWithCredential(UserFullInfo):
    username: str
    password: HashedPassword


class UserRegisterData(UserFullInfo):
    # password: str  # type: ignore
    # we fill password automatic
    pass


class FullUser(UserWithCredential):
    id: int
    role: UserRole


class FullAdmin(BaseModel):
    full_user: UserFullInfo


class ObjectAdded(BaseModel):
    code: AddCode
    message: AddMessage


class ObjectDeleted(BaseModel):
    code: DeleteCode
    message: DeleteMessage
