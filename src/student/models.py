import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

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


class StudentCourse(BaseModel):
    __tablename__ = "student_course"

    student_id: Mapped[StudnentID] = mapped_column(
        ForeignKey("student.id"), primary_key=True, nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("course.id"), primary_key=True, nullable=False
    )
