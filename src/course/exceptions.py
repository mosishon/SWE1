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


class SectionNotFound(BaseError):
    code: Literal[ErrorCode.SECTION_NOT_FOUND] = ErrorCode.SECTION_NOT_FOUND
    details: Literal["Seciton not found."] = "Seciton not found."


class SectionCountValue(BaseError):
    code: Literal[
        ErrorCode.SECTION_COUNT_MORE_THAN_ZERO
    ] = ErrorCode.SECTION_COUNT_MORE_THAN_ZERO
    details: Literal[
        "Section count value should be more than zero."
    ] = "Section count value should be more than zero."
