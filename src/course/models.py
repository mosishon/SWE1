from typing import List

from sqlalchemy import SMALLINT, Enum, ForeignKey, PrimaryKeyConstraint, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.course.schemas import DayOfWeek
from src.models import BaseModel


class CourseSectionToInstructorAssociation(BaseModel):
    __tablename__ = "coursesection_to_instructor"
    course_section_id: Mapped[int] = mapped_column(
        ForeignKey("course_section.id", ondelete="CASCADE"), primary_key=True
    )
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("instructor.id", ondelete="CASCADE"), primary_key=True
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
from src.instructor.models import Instructor


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

    instructors: Mapped[List["Instructor"]] = relationship(
        "Instructor",
        secondary="coursesection_to_instructor",
        back_populates="available_times",
    )

    courses: Mapped[List["Course"]] = relationship(
        "Course",
        secondary="coursesection_to_course",
        back_populates="sections",
    )
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
    instructor_id: Mapped[Instructor] = mapped_column(
        ForeignKey("instructor.id"), index=True
    )
    instructor: Mapped[Instructor] = relationship(back_populates="assigned_courses")
    sections_count: Mapped[int] = mapped_column(SMALLINT)
    unit: Mapped[int] = mapped_column(SMALLINT)
    importance: Mapped[int] = mapped_column()
    # sections: Mapped[list[CourseSection]] = relationship(
    #     back_populates="courses", secondary=CourseSectionToCourseAssociation
    # )
    sections: Mapped[List["CourseSection"]] = relationship(
        "CourseSection",
        secondary="coursesection_to_course",
        back_populates="courses",
    )

    students: Mapped[List["Student"]] = relationship(  # type: ignore
        "Student", secondary="reserved_course", back_populates="reserved_courses"
    )
    # instructors: Mapped[list["Instructor"]] = relationship(  # type: ignore
    #     "Instructor", secondary="course_instructor", back_populates="assigned_courses"
    # )
