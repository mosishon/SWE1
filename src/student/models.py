from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.cutsom_types import StudnentID
from src.models import BaseModel


# NOT FULL VERSION
class Student(BaseModel):
    __tablename__ = "student"
    student_id: Mapped[StudnentID] = mapped_column(
        primary_key=True, index=True, unique=True, nullable=False
    )
    for_user: Mapped[int] = mapped_column(
        ForeignKey("user.id"), index=True, nullable=False
    )
