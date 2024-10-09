import datetime
import enum

from sqlalchemy import BigInteger, Enum, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.cutsom_types import HashedPassword, NationalID, PhoneNumber, StudnentID


class BaseModel(DeclarativeBase):
    type_annotation_map = {
        StudnentID: BigInteger(),
        NationalID: BigInteger(),
        PhoneNumber: BigInteger(),
        HashedPassword: String(),
    }
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class UserRole(enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"
    Instructor = "instructor"


class User(BaseModel):
    __tablename__ = "user"
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    national_id: Mapped[NationalID] = mapped_column(index=True)
    email: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(index=True)
    phone_number: Mapped[PhoneNumber] = mapped_column()
    birth_day: Mapped[datetime.datetime] = mapped_column()
    password: Mapped[HashedPassword] = mapped_column()
    role: Mapped[str] = mapped_column(Enum(UserRole))
