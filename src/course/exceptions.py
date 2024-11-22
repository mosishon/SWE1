from typing import Literal

from src.schemas import BaseError, ErrorCode


class SectionExists(BaseError):
    code: Literal[ErrorCode.SECTION_EXSISTS] = ErrorCode.SECTION_EXSISTS
    details: Literal["Section already exists"] = "Section already exists"


class CourseExists(BaseError):
    code: Literal[ErrorCode.COURSE_EXSISTS] = ErrorCode.COURSE_EXSISTS
    details: Literal["Course already exists"] = "Course already exists"


class CourseNotFound(BaseError):
    code: Literal[ErrorCode.COURSE_NOT_FOUND] = ErrorCode.COURSE_NOT_FOUND
    details: Literal["Course not found."] = "Course not found."
