import datetime
from enum import Enum
from typing import List, NewType, Tuple

from pydantic import BaseModel, model_validator

from src.exceptions import InstructorTimeIsFull

HashedPassword = NewType("HashedPassword", str)
CourseSectionTime = NewType("CourseSectionTime", datetime.time)


class DayOfWeek(int, Enum):
    shanbe = 0
    yek_shanbe = 0
    ...


class CourseSectionCount(int, Enum):
    one = 1
    two = 2


class User(BaseModel):
    first_name: str
    last_name: str
    password: HashedPassword


class CourseSection(BaseModel):
    week_day: DayOfWeek
    start_time: CourseSectionTime
    end_time: CourseSectionTime


class Instructor(BaseModel):
    first_name: str
    last_name: str
    available_course_sections: List[CourseSection]
    courses: List["Course"]

    @model_validator
    def validate_courses_and_available_times(cls, values):
        sections_need = sum(map(lambda x: x.sections_count, values["courses"]))
        sections_have = len(values["available_course_sections"])
        if sections_need > sections_have:
            raise InstructorTimeIsFull("test")
        return cls


class Course(BaseModel):
    name: str
    short_name: str
    instructor: Instructor
    sections_count: CourseSectionCount
    unit: int
    importance: int
    sections: Tuple[CourseSection]
