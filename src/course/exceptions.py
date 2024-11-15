from typing import Literal

from src.schemas import BaseError, ErrorCode


class SectionExists(BaseError):
    code: Literal[ErrorCode.SECTION_EXSISTS] = ErrorCode.SECTION_EXSISTS
    details: Literal["Section already exists"] = "Section already exists"


class CourseExists(BaseError):
    code: Literal[ErrorCode.COURSE_EXSISTS] = ErrorCode.COURSE_EXSISTS
    details: Literal["Course already exists"] = "Course already exists"
