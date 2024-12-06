from sqlalchemy import SMALLINT, Enum, ForeignKey, PrimaryKeyConstraint, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.course.schemas import DayOfWeek
from src.models import BaseModel


class CourseSectionToInstructorAssociation(BaseModel):
    __tablename__ = "coursesection_to_instructor"
    course_section_id: Mapped[int] = mapped_column(
        ForeignKey("course_section.id"), primary_key=True
    )
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("instructor.id"), primary_key=True
    )


class CourseSectionToCourseAssociation(BaseModel):
    __tablename__ = "coursesection_to_course"
    course_id: Mapped[int] = mapped_column(
        ForeignKey("course.id", ondelete="CASCADE"), primary_key=True
    )
    course_section_id: Mapped[int] = mapped_column(
        ForeignKey("course_section.id", ondelete="CASCADE"), primary_key=True
    )


# NOT FULL VERSION
# دقت کنید که کورسی که در این قسمت تعریف شده
# کورسی است که بعد از چیده شدن برنامه به این ساعت از روز تخصیص داده شده


# چندین استاد متفاوت ممکنه توی یک ساعت کلاس داشته باشن.
# مهم اینه یه استاد ثابت توی یک ساعت چند کلاس نداشته باشه
class CourseSection(BaseModel):
    __tablename__ = "course_section"
    id: Mapped[int] = mapped_column(autoincrement=True, unique=True)
    day_of_week: Mapped[int] = mapped_column(Enum(DayOfWeek))
    start_time: Mapped[int] = mapped_column(SmallInteger())
    end_time: Mapped[int] = mapped_column(SmallInteger())
    # courses: Mapped[list["Course"]] = relationship(
    #     back_populates="sections", secondary=CourseSectionToCourseAssociation
    # )
    # empty_for_instructor: Mapped[list[Instructor]] = relationship(
    #     back_populates="available_course_sections",
    #     secondary=CourseSectionToInstructorAssociation,
    # )

    __table_args__ = (
        PrimaryKeyConstraint("id", "day_of_week", "start_time", "end_time"),
    )


class Course(BaseModel):
    __tablename__ = "course"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(primary_key=True)
    short_name: Mapped[str] = mapped_column(primary_key=True)
    group: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    # instructor_id: Mapped[User] = mapped_column(ForeignKey("instructor.id"), index=True)
    # instructor: Mapped[Instructor] = relationship(back_populates="assigned_courses")
    sections_count: Mapped[int] = mapped_column(SMALLINT)
    unit: Mapped[int] = mapped_column(SMALLINT)
    importance: Mapped[int] = mapped_column()
    # sections: Mapped[list[CourseSection]] = relationship(
    #     back_populates="courses", secondary=CourseSectionToCourseAssociation
    # )
