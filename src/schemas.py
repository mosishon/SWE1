import enum

from pydantic import BaseModel, EmailStr, PastDate

from src.cutsom_types import HashedPassword, NationalID, PhoneNumber


class SuccessCodes(str, enum.Enum):
    STUDENT_ADDED = "STUDENT_ADDED"
    STUDENT_DELETED = "STUDENT_DELETED"
    PASSWORD_RESETED = "PASSWORD_RESETED"


class Messages(str, enum.Enum):
    STUDENT_ADDED = "Student added successfully"
    STUDENT_DELETED = "Student deleted successfully"


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    STUDENT = "STUDENT"
    INSTRUCTOR = "INSTRUCTOR"


class ErrorCode(str, enum.Enum):
    COURSE_NOT_FOUND = "COURSE_NOT_FOUND"
    STUDENT_NOT_FOUND = "STUDENT_NOT_FOUND"
    STUDENT_DUPLICATE = "STUDENT_DUPLICATE"
    INVALID_EMAIL = "INVALID_EMAIL"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_RESET_LINK = "INVALID_RESET_LINK"
    PASSWORDS_NOT_SAME = "PASSWORDS_NOT_SAME"


class BaseUser(BaseModel):
    first_name: str
    last_name: str
    birth_day: PastDate


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
    code: SuccessCodes
    message: Messages


class ObjectDeleted(BaseModel):
    code: SuccessCodes
    message: Messages


class BaseError(BaseModel):
    code: ErrorCode
    details: str
