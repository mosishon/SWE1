from sqlalchemy.orm import DeclarativeBase

from src.authentication.models import Token
from src.student.models import Student


class BaseModel(DeclarativeBase):
    pass


__all__ = ["Token", "Student"]
