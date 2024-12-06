import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.cutsom_types import HashedPassword, NationalID, PhoneNumber
from src.models import BaseModel


class CourseInstructor(BaseModel):
    __tablename__ = "course_instructor"

    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("instructor.id", ondelete="CASCADE"), primary_key=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("course.id", ondelete="CASCADE"), primary_key=True
    )


class Instructor(BaseModel):
    __tablename__ = "instructor"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
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
    # available_course_sections: Mapped[list["CourseSection"]] = relationship(
    #     back_populates="empty_for_instructor",
    #     secondary="CourseSectionToInstructorAssociation",
    # )
    # assigned_courses: Mapped[list["Course"]] = relationship(back_populates="instructor")
