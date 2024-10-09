import datetime

from sqlalchemy.orm import Mapped, mapped_column

from src.cutsom_types import HashedPassword, NationalID, PhoneNumber, StudnentID
from src.models import BaseModel


# NOT FULL VERSION
class Student(BaseModel):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    national_id: Mapped[NationalID] = mapped_column()
    student_id: Mapped[StudnentID] = mapped_column()
    email: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column()
    phone_number: Mapped[PhoneNumber] = mapped_column()
    birth_day: Mapped[datetime.datetime] = mapped_column()
    password: Mapped[HashedPassword] = mapped_column()
