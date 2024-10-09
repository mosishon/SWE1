import datetime
from typing import NewType

from pydantic import BaseModel, EmailStr

HashedPassword = NewType("HashedPassword", str)
PhoneNumber = NewType("PhoneNumber", int)
NationalID = NewType("NationalID", int)
StudnentID = NewType("StudnentID", int)


class Student(BaseModel):
    first_name: str
    last_name: str
    national_id: NationalID
    student_id: StudnentID
    email: EmailStr
    username: str
    phone_number: PhoneNumber
    birth_day: datetime.datetime
    password: HashedPassword
