import enum

from pydantic import BaseModel, EmailStr, NaiveDatetime

from src.cutsom_types import HashedPassword, NationalID, PhoneNumber


class UserRole(enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"
    INSTRUCTOR = "instructor"


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


class UserRegisterData(UserWithCredential):
    password: str  # type: ignore


class FullUser(UserWithCredential):
    id: int
    role: UserRole
