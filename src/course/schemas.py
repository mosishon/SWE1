import datetime
from enum import IntEnum
from typing import Literal, NewType, Tuple

from pydantic import BaseModel, ValidationInfo, field_validator

from src.instructor.schemas import FullInstructor
from src.schemas import FullUser, Messages, ObjectAdded, SuccessCodes

CourseSectionTime = NewType("CourseSectionTime", datetime.time)


class DayOfWeek(IntEnum):
    shanbe = 0
    yek_shanbe = 1
    do_shanbe = 2
    se_shanbe = 3
    char_shanbe = 4
    panj_shanbe = 5
    jome = 6


class CourseSectionCount(IntEnum):
    one = 1
    two = 2


class Unit(IntEnum):
    one = 1
    two = 2
    three = 3


class CourseSection(BaseModel):
    day_of_week: DayOfWeek
    start_time: CourseSectionTime
    end_time: CourseSectionTime

    class Config:
        from_attributes = True


class Course(BaseModel):
    name: str
    short_name: str
    instructor: FullInstructor
    sections_count: CourseSectionCount
    unit: Unit
    importance: int
    sections: Tuple[CourseSection]


class AddCourseIn(BaseModel):
    name: str
    short_name: str
    instructor_id: int | None
    section_count: int
    unit: int
    group: int
    importance: int
    sections_id: list[int]


class AddCourseOut(BaseModel):
    course_name: str


class AddSectionIn(BaseModel):
    week_day: DayOfWeek
    start_time: int
    end_time: int

    @field_validator("start_time")
    def st(cls, v: int, info: ValidationInfo) -> int:
        if v < 8 or v > 20:
            raise ValueError("invalid time")

        return v

    @field_validator("end_time")
    def et(cls, v: int, info: ValidationInfo) -> int:
        if v < 8 or v > 20:
            raise ValueError("invalid time")
        if abs(v - info.data["start_time"]) != 2:
            raise ValueError("delta times should be 2")
        return v

    class Config:
        # JSON encoder for HexColor
        json_encoders = {
            CourseSectionTime: lambda v: datetime.date(v.year, v.month, v.day)
        }


class SectionCreated(ObjectAdded):
    code: Literal[SuccessCodes.SECTION_ADDED] = SuccessCodes.SECTION_ADDED
    message: Literal[Messages.SECTION_ADDED] = Messages.SECTION_ADDED
    section_id: int


class CourseCreated(ObjectAdded):
    code: Literal[SuccessCodes.COURSE_ADDED] = SuccessCodes.COURSE_ADDED
    message: Literal[Messages.COURSE_ADDED] = Messages.COURSE_ADDED
    course_id: int


class AllCoursesInstructor(BaseModel):
    instructor_id: int
    full_user: FullUser


class AllCoursesCourse(BaseModel):
    name: str
    short_name: str
    sections_count: CourseSectionCount
    unit: Unit
    importance: int
    sections: list[CourseSection]
    instructor: AllCoursesInstructor


class AllCoursesOut(BaseModel):
    courses: list[AllCoursesCourse]
    count: int
