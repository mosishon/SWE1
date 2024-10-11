from pydantic import BaseModel, EmailStr, datetime

from src.cutsom_types import (
    HashedPassword,
    NationalID,
    PhoneNumber,
    StudnentID,
    TimeStamp,
)


# NOT FULL VERSION
class TokenData(BaseModel):
    user_id: int
    exp: TimeStamp


class Token(BaseModel):
    token: str


class LoginData(BaseModel):
    username: str
    password: HashedPassword


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    student_id: StudnentID
    email: EmailStr
    username: str

    class Config:
        orm = True


class StudentIn(StudentBase):
    national_id: NationalID
    phone_number: PhoneNumber
    birth_day: datetime.date
    password: HashedPassword


class StudentOut(StudentBase):
    pass
