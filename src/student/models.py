from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.cutsom_types import StudnentID
from src.models import BaseModel


# NOT FULL VERSION
class StudentOptions(BaseModel):
    __tablename__ = "student_options"
    student_id: Mapped[StudnentID] = mapped_column(index=True)

    for_user: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
