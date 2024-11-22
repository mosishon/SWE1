from typing import Literal

from src.schemas import BaseError, ErrorCode


class InvalidEmail(BaseError):
    code: Literal[ErrorCode.INVALID_EMAIL] = ErrorCode.INVALID_EMAIL
    details: Literal["Invalid Email address"] = "Invalid Email address"


class StudentDuplicate(BaseError):
    code: Literal[ErrorCode.STUDENT_DUPLICATE] = ErrorCode.STUDENT_DUPLICATE
    details: Literal["student is duplicate."] = "student is duplicate."
    duplicate_fields: list[str]


class StudentNotFound(BaseError):
    code: Literal[ErrorCode.STUDENT_NOT_FOUND] = ErrorCode.STUDENT_NOT_FOUND
    details: Literal["student not found."] = "student not found."
