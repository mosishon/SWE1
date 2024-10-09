from typing import List

from pydantic import BaseModel, model_validator

from exceptions import InstructorTimeIsFull
from src.course.schemas import Course, CourseSection
from src.cutsom_types import HashedPassword


class Instructor(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: HashedPassword
    available_course_sections: List[CourseSection]
    courses: List[Course]

    @model_validator(mode="before")
    def validate_courses_and_available_times(cls, values) -> "Instructor":
        sections_need = sum(map(lambda x: x.sections_count, values["courses"]))
        sections_have = len(values["available_course_sections"])
        if sections_need > sections_have:
            raise InstructorTimeIsFull("test")
        return cls
