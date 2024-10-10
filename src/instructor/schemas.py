from typing import TYPE_CHECKING

from pydantic import BaseModel, model_validator

from src.instructor.exceptions import InstructorTimeIsFull, UserIsNotInstructor
from src.schemas import FullUser, UserRole

if TYPE_CHECKING:
    from src.course.schemas import CourseSection


class FullInstructor(BaseModel):
    full_user: FullUser
    available_course_sections: list["CourseSection"]

    @model_validator(mode="before")
    def validate_courses_and_available_times(cls, values) -> "FullInstructor":
        sections_need = sum(map(lambda x: x.sections_count, values["courses"]))
        sections_have = len(values["available_course_sections"])
        if sections_need > sections_have:
            raise InstructorTimeIsFull("test")
        elif values["full_user"].role != UserRole.Instructor:
            raise UserIsNotInstructor("test")
        return cls
