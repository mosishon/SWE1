import datetime
from enum import Enum
from typing import NewType, Tuple

from pydantic import BaseModel

from src.instructor.schemas import Instructor

CourseSectionTime = NewType("CourseSectionTime", datetime.time)


class DayOfWeek(int, Enum):
    shanbe = 0
    yek_shanbe = 1
    ...


class CourseSectionCount(int, Enum):
    one = 1
    two = 2


class CourseSection(BaseModel):
    week_day: DayOfWeek
    start_time: CourseSectionTime
    end_time: CourseSectionTime


class Course(BaseModel):
    name: str
    short_name: str
    instructor: Instructor
    sections_count: CourseSectionCount
    unit: int
    importance: int
    sections: Tuple[CourseSection]
