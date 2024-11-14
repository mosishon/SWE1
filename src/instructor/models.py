from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models import BaseModel


class Instructor(BaseModel):
    __tablename__ = "instructor"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)

    # available_course_sections: Mapped[list["CourseSection"]] = relationship(
    #     back_populates="empty_for_instructor",
    #     secondary="CourseSectionToInstructorAssociation",
    # )
    # assigned_courses: Mapped[list["Course"]] = relationship(back_populates="instructor")
    for_user: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
