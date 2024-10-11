import datetime
import enum

from pydantic import BaseModel, EmailStr

from src.cutsom_types import HashedPassword, NationalID, PhoneNumber


class UserRole(enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"
    Instructor = "instructor"


class FullUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    national_id: NationalID
    email: EmailStr
    username: str
    phone_number: PhoneNumber
    birth_day: datetime.datetime
    password: HashedPassword
    role: UserRole
