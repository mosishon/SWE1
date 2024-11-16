import datetime
import re
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, EmailStr, PastDate, ValidationInfo, field_validator

from src.cutsom_types import NationalID
from src.schemas import Messages, SuccessCodes

if TYPE_CHECKING:
    pass


class InstuctorSchema(BaseModel):
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

    # @model_validator(mode="before")
    # def validate_courses_and_available_times(cls, values) -> "FullInstructor":
    #     sections_need = sum(map(lambda x: x.sections_count, values["courses"]))
    #     sections_have = len(values["available_course_sections"])
    #     if sections_need > sections_have:
    #         raise InstructorTimeIsFull("test")
    #     elif values["full_user"].role != UserRole.INSTRUCTOR:
    #         raise UserIsNotInstructor("test")
    #     return cls


def is_valid_iran_code(input: str) -> bool:
    if not re.search(r"^\d{10}$", input):
        return False
    check = int(input[9])
    s = sum(int(input[x]) * (10 - x) for x in range(9)) % 11
    return check == s if s < 2 else check + s == 11


class AddInstructorIn(BaseModel):
    first_name: str
    last_name: str
    national_id: NationalID
    email: EmailStr
    birth_day: PastDate
    phone_number: str

    @field_validator("national_id")
    def national_id_valid(cls, v: str, info: ValidationInfo) -> str:
        # valid = is_valid_iran_code(v)
        # if valid is False:
        #     raise ValueError("invalid natinal code")
        return v

    @field_validator("phone_number")
    def phone_number_valid(cls, v: str, info: ValidationInfo) -> str:
        pn = v.strip().replace(" ", "")
        if not pn.isdigit() or len(pn) != 11:
            raise ValueError("invalid phone number. format: 09170000000")
        return pn


class InstructorSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    national_id: NationalID
    email: EmailStr
    username: str
    phone_number: str
    birth_day: datetime.date

    class Config:
        from_attributes = True


class InstructorCreated(BaseModel):
    code: Literal[SuccessCodes.INSTRUCTOR_ADDED] = SuccessCodes.INSTRUCTOR_ADDED
    message: Literal[Messages.INSTRUCTOR_ADDED] = Messages.INSTRUCTOR_ADDED
    instuctor: InstructorSchema
