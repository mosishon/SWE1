import datetime
from enum import Enum
from typing import NewType, Tuple

from pydantic import BaseModel

from src.instructor.schemas import FullInstructor

CourseSectionTime = NewType("CourseSectionTime", datetime.time)


class DayOfWeek(int, Enum):
    shanbe = 0
    yek_shanbe = 1
    ...


class CourseSectionCount(int, Enum):
    one = 1
    two = 2


class Unit(int, Enum):
    one = 1
    two = 2
    three = 3


class CourseSection(BaseModel):
    week_day: DayOfWeek
    start_time: CourseSectionTime
    end_time: CourseSectionTime


class Course(BaseModel):
    name: str
    short_name: str
    instructor: FullInstructor
    sections_count: CourseSectionCount
    unit: Unit
    importance: int
    sections: Tuple[CourseSection]


class AddCourseIn(BaseModel):
    course_name: str
    course_id: int


class AddCourseOut(BaseModel):
    course_name: str
