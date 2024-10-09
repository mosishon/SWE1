import datetime

from pydantic import BaseModel, EmailStr

from src.cutsom_types import HashedPassword, NationalID, PhoneNumber, StudnentID


class FullUser(BaseModel):
    first_name: str
    last_name: str
    national_id: NationalID
    student_id: StudnentID
    email: EmailStr
    username: str
    phone_number: PhoneNumber
    birth_day: datetime.datetime
    password: HashedPassword
