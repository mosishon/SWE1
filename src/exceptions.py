from typing import Literal

from pydantic import BaseModel

from src.schemas import BaseError, ErrorCode


class InstructorTimeIsFull(BaseException):
    pass


class GlobalException(Exception):
    def __init__(self, model: BaseModel, status_code: int):
        self.model = model
        self.status_code = status_code


class UnknownError(BaseError):
    code: Literal[ErrorCode.UNKNOWN_ERROR] = ErrorCode.UNKNOWN_ERROR
    details: Literal[
        "Something Unexpected, Server Error"
    ] = "Something Unexpected, Server Error"
