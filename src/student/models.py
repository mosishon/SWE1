import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.course.models import Course
from src.cutsom_types import HashedPassword, NationalID, PhoneNumber, StudnentID
from src.models import BaseModel


# NOT FULL VERSION
class Student(BaseModel):
    __tablename__ = "student"
    id: Mapped[StudnentID] = mapped_column(
        primary_key=True, index=True, unique=True, nullable=False
    )
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    national_id: Mapped[NationalID] = mapped_column(
        primary_key=True, index=True, unique=True
    )
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(index=True, unique=True)
    phone_number: Mapped[PhoneNumber] = mapped_column(unique=True)
    birth_day: Mapped[datetime.date] = mapped_column()
    password: Mapped[HashedPassword] = mapped_column(nullable=False)
    reserved_courses: Mapped[List["Course"]] = relationship(
        "Course", secondary="reserved_course", back_populates="students"
    )


class ReservedCourse(BaseModel):
    __tablename__ = "reserved_course"

    student_id: Mapped[StudnentID] = mapped_column(
        ForeignKey("student.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("course.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
