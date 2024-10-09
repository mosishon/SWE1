from sqlalchemy.orm import Mapped, relationship

from src.course.models import CourseSection
from src.models import User


class Instructor(User):
    __tablename__ = "instructor"
    available_course_sections: Mapped[list[CourseSection]] = relationship(
        back_populates="course_section.id"
    )
