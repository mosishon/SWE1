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


class StudentCourse(BaseModel):
    __tablename__ = "student_course"

    student_id: Mapped[StudnentID] = mapped_column(
        ForeignKey("student.student_id"), primary_key=True, nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("course.id"), primary_key=True, nullable=False
    )
