from typing import Literal

from src.schemas import BaseError, ErrorCode


class InvalidEmail(BaseError):
    code: Literal[ErrorCode.INVALID_EMAIL] = ErrorCode.INVALID_EMAIL
    details: Literal["Invalid Email address"] = "Invalid Email address"


class InvalidResetLink(BaseError):
    code: Literal[ErrorCode.INVALID_RESET_LINK] = ErrorCode.INVALID_RESET_LINK
    details: Literal[
        "Invalid Password Reset Payload or Reset Link Expired"
    ] = "Invalid Password Reset Payload or Reset Link Expired"


class PasswordsDoseNotMatch(BaseError):
    code: Literal[ErrorCode.PASSWORDS_NOT_SAME] = ErrorCode.PASSWORDS_NOT_SAME
    details: Literal[
        "New password and confirm password are not same."
    ] = "New password and confirm password are not same."
