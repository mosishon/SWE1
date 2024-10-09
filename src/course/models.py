from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, Table
from sqlalchemy.orm import Mapped, mapped_column

from src.models import BaseModel


# NOT FULL VERSION
class CourseSection(BaseModel):
    __tablename__ = "course_section"

    day_of_week: Mapped[int] = mapped_column(SmallInteger())
    start_time: Mapped[int] = mapped_column(SmallInteger())
    end_time: Mapped[int] = mapped_column(SmallInteger())


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
