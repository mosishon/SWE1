from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.course.models import CourseSectionToInstructorAssociation
from src.models import BaseModel

if TYPE_CHECKING:
    from src.course.models import Course, CourseSection


class Instructor(BaseModel):
    __tablename__ = "instructor"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)

    available_course_sections: Mapped[list["CourseSection"]] = relationship(
        back_populates="empty_for_instructor",
        secondary=CourseSectionToInstructorAssociation,
    )
    assigned_courses: Mapped[list["Course"]] = relationship(back_populates="instructor")
    for_user: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
