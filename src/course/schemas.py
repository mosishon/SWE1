import datetime
from enum import IntEnum
from typing import List, Literal, NewType, Optional

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from src.schemas import Messages, ObjectAdded, ObjectDeleted, SuccessCodes

CourseSectionTime = NewType("CourseSectionTime", int)


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


class CourseSectionSchema(BaseModel):
    id: int
    day_of_week: DayOfWeek
    start_time: CourseSectionTime
    end_time: CourseSectionTime

    class Config:
        from_attributes = True


from src.instructor.schemas import InstructorSchema


class CourseSchema(BaseModel):
    id: int
    name: str
    short_name: str
    instructor: InstructorSchema
    sections_count: CourseSectionCount
    unit: Unit
    importance: int
    sections: list[CourseSectionSchema]

    class Config:
        from_attributes = True


class CourseInfoSchema(BaseModel):
    name: str
    short_name: str
    sections_count: CourseSectionCount
    unit: Unit
    importance: int

    class Config:
        from_attributes = True


class AddCourseIn(BaseModel):
    name: str
    short_name: str
    instructor_id: int | None
    section_count: int
    unit: int
    group: int
    importance: int
    sections_id: list[int]


class ReserveCourseIn(BaseModel):
    course_id: int = Field(gt=0)


class UnReservedCourseIn(BaseModel):
    course_id: int = Field(gt=0)


class DeleteCourse(BaseModel):
    course_id: int


class CourseUnreserved(BaseModel):
    name: str
    short_name: str
    group: int
    unit: int


class AddCourseOut(BaseModel):
    course: CourseSchema


class CourseReserved(BaseModel):
    course: CourseInfoSchema
    code: Literal[SuccessCodes.COURSE_RESERVED] = SuccessCodes.COURSE_RESERVED


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


class AllCoursesOut(BaseModel):
    courses: list[CourseSchema]
    count: int


class CourseDeleted(ObjectDeleted):
    code: Literal[SuccessCodes.COURSE_DELETED] = SuccessCodes.COURSE_DELETED
    message: Literal[Messages.COURSE_DELETED] = Messages.COURSE_DELETED
    course: CourseInfoSchema


class DeleteSectionIn(BaseModel):
    section_id: int = Field(gt=0)


class SectionDeleted(ObjectDeleted):
    code: Literal[SuccessCodes.SECTION_DELETED] = SuccessCodes.SECTION_DELETED
    message: Literal[Messages.SECTION_DELETED] = Messages.SECTION_DELETED
    section: CourseSectionSchema


class ListSections(BaseModel):
    sections: List[CourseSectionSchema]
    count: int


class UpdateCourseIn(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    unit: Optional[int] = None
    importance: Optional[int] = None
    group: Optional[int] = None
    is_active: Optional[bool] = None
