from typing import Literal

from src.schemas import BaseError, ErrorCode


class SectionExists(BaseError):
    code: Literal[ErrorCode.SECTION_EXSISTS] = ErrorCode.SECTION_EXSISTS
    details: Literal["Section already exists"] = "Section already exists"
