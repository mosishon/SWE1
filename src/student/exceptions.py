from typing import Literal

from src.schemas import BaseError, ErrorCode


class InvalidEmail(BaseError):
    code: Literal[ErrorCode.INVALID_EMAIL] = ErrorCode.INVALID_EMAIL
    details: Literal["Invalid Email address"] = "Invalid Email address"


class CourseNotFound(BaseError):
    code: Literal[ErrorCode.COURSE_NOT_FOUND] = ErrorCode.COURSE_NOT_FOUND
    details: Literal["course not found."] = "course not found."
