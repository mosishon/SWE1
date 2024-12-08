import datetime
import enum

from pydantic import BaseModel, EmailStr, PastDate

from src.cutsom_types import HashedPassword, NationalID, PhoneNumber


class SuccessCodes(str, enum.Enum):
    STUDENT_ADDED = "STUDENT_ADDED"
    STUDENT_DELETED = "STUDENT_DELETED"
    PASSWORD_RESETED = "PASSWORD_RESETED"
    SECTION_ADDED = "SECTION_ADDED"
    COURSE_ADDED = "COURSE_ADDED"
    INSTRUCTOR_ADDED = "INSTRUCTOR_ADDED"
    SECTION_ENROLLED = "SECTION_ENROLLED"
    INSTRUCTOR_DELETED = "INSTRUCTOR_DELETED"
    COURSE_DELETED = "COURSE_DELETED"
    SECTION_DELETED = "SECTION_DELETED"
    COURSE_RESERVED = "COURSE_RESERVED"
    COURSE_UNRESERVED = "COURSE_UNRESERVED"


class Messages(str, enum.Enum):
    STUDENT_ADDED = "Student added successfully"
    INSTRUCTOR_ADDED = "Instructor added successfully"
    SECTION_ENROLLED = "Section enrolled successfully"
    STUDENT_DELETED = "Student deleted successfully"
    INSTRUCTOR_DELETED = "Instructor deleted successfully"
    COURSE_DELETED = "Course deleted successfully"
    SECTION_DELETED = "Section deleted successfully"
    SECTION_ADDED = "Section added successfully"
    COURSE_ADDED = "Course added successfully"


class UserRole(enum.StrEnum):
    ADMIN = "ADMIN"
    STUDENT = "STUDENT"
    INSTRUCTOR = "INSTRUCTOR"
    ALL = "ALL"


class ErrorCode(str, enum.Enum):
    COURSE_NOT_FOUND = "COURSE_NOT_FOUND"
    SECTION_NOT_FOUND = "SECTION_NOT_FOUND"
    STUDENT_NOT_FOUND = "STUDENT_NOT_FOUND"
    STUDENT_DUPLICATE = "STUDENT_DUPLICATE"
    INVALID_EMAIL = "INVALID_EMAIL"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_RESET_LINK = "INVALID_RESET_LINK"
    PASSWORDS_NOT_SAME = "PASSWORDS_NOT_SAME"
    SECTION_EXSISTS = "SECTION_EXSISTS"
    COURSE_EXSISTS = "COURSE_EXSISTS"
    ACCESS_DENIED = "ACCESS_DENIED"
    INSTRUCTOR_NOT_FOUND = "INSTRUCTOR_NOT_FOUND"
    ALREADY_RESERVED = "ALREADY_RESERVED"
    SECTION_COUNT_MORE_THAN_ZERO = "SECTION_COUNT_MORE_THAN_ZERO"
    COURSE_UNIT_MORE_THAN_ZERO = "COURSE_UNIT_MORE_THAN_ZERO"
    SECTION_ALREADY_ENROLLED = "SECTION_ALREADY_ENROLLED"


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


class AdminSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    national_id: str
    email: EmailStr
    username: str
    phone_number: str
    birth_day: datetime.date

    class Config:
        from_attributes = True


class ObjectAdded(BaseModel):
    code: SuccessCodes
    message: Messages


class ObjectDeleted(BaseModel):
    code: SuccessCodes
    message: Messages


class BaseError(BaseModel):
    code: ErrorCode
    details: str
