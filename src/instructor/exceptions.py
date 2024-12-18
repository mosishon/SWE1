from typing import Literal

from src.schemas import BaseError, ErrorCode


class InstructorTimeIsFull(BaseException):
    pass


class UserIsNotInstructor(BaseException):
    pass


class InstructorNotFound(BaseError):
    code: Literal[ErrorCode.INSTRUCTOR_NOT_FOUND] = ErrorCode.INSTRUCTOR_NOT_FOUND
    details: Literal["Instructor not found."] = "Instructor not found."


class SectionAlreadyEnrolled(BaseError):
    code: Literal[
        ErrorCode.SECTION_ALREADY_ENROLLED
    ] = ErrorCode.SECTION_ALREADY_ENROLLED
    details: Literal["Section already enrolled."] = "Section already enrolled."
