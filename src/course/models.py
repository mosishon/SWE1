from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    SmallInteger,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.course.schemas import CourseSectionCount, DayOfWeek, Unit
from src.models import BaseModel, User

CourseSectionToInstructorAssociation = Table(
    "coursesection_to_instructor",
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

CourseSectionToCourseAssociation = Table(
    "coursesection_to_course",
    BaseModel.metadata,
    Column(
        "course_id",
        Integer,
        ForeignKey("course.id"),
        nullable=False,
        primary_key=True,
    ),
    Column(
        "course_section_id",
        Integer,
        ForeignKey("course_section.id"),
        nullable=False,
        primary_key=True,
    ),
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

    __table_args__ = (PrimaryKeyConstraint("day_of_week", "start_time", "end_time"),)


class Course(BaseModel):
    __tablename__ = "course"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)

    name: Mapped[str] = mapped_column()
    short_name: Mapped[str] = mapped_column()
    instructor_id: Mapped[User] = mapped_column(ForeignKey("instructor.id"), index=True)
    # instructor: Mapped[Instructor] = relationship(back_populates="assigned_courses")
    sections_count: Mapped[int] = mapped_column(Enum(CourseSectionCount))
    unit: Mapped[int] = mapped_column(Enum(Unit))
    importance: Mapped[int] = mapped_column()
    # sections: Mapped[list[CourseSection]] = relationship(
    #     back_populates="courses", secondary=CourseSectionToCourseAssociation
    # )
