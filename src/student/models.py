from sqlalchemy.orm import Mapped, mapped_column

from src.cutsom_types import StudnentID
from src.models import User


# NOT FULL VERSION
class Student(User):
    __tablename__ = "user"
    student_id: Mapped[StudnentID] = mapped_column(index=True)
