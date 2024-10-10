from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseModel, User

if TYPE_CHECKING:
    from src.instructor.models import Instructor

CourseSectionAssociation = Table(
    "course_to_instructor",
    BaseModel.metadata,
    Column(
        "course_section_id",
        Integer,
        ForeignKey("course_section.id"),
        nullable=False,
        primary_key=True,
    ),
    Column(
        "instructor_id",
        Integer,
        ForeignKey("instructor.id"),
        nullable=False,
        primary_key=True,
    ),
)


# NOT FULL VERSION
class CourseSection(BaseModel):
    __tablename__ = "course_section"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)

    day_of_week: Mapped[int] = mapped_column(SmallInteger())
    start_time: Mapped[int] = mapped_column(SmallInteger())
    end_time: Mapped[int] = mapped_column(SmallInteger())
    course: Mapped[int] = mapped_column(ForeignKey("course.id"), index=True)
    empty_for_instructor: Mapped[list["Instructor"]] = relationship(
        back_populates="available_course_sections", secondary=CourseSectionAssociation
    )


class Course(BaseModel):
    __tablename__ = "course"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)

    name: Mapped[str] = mapped_column()
    short_name: Mapped[str] = mapped_column()
    instructor: Mapped[User] = mapped_column(ForeignKey("instructor.id"), index=True)
    sections_count: Mapped[int] = mapped_column()
    unit: Mapped[int] = mapped_column()
    importance: Mapped[int] = mapped_column()
    sections: Mapped[CourseSection] = relationship(back_populates="course")
