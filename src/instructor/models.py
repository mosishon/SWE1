from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.course.models import CourseSection
from src.models import BaseModel


class InstructorOptions(BaseModel):
    __tablename__ = "Instructor_options"
    available_course_sections: Mapped[list[CourseSection]] = relationship(
        back_populates="course_section.id"
    )

    for_user: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
