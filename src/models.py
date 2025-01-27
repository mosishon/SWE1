import datetime

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.cutsom_types import HashedPassword, NationalID, PhoneNumber, StudnentID


class BaseModel(DeclarativeBase):
    type_annotation_map = {
        StudnentID: String(),
        NationalID: String(),
        PhoneNumber: String(),
        HashedPassword: String(),
    }


class Admin(BaseModel):
    __tablename__ = "admin"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    national_id: Mapped[NationalID] = mapped_column(
        primary_key=True, index=True, unique=True
    )
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(index=True, unique=True)
    phone_number: Mapped[PhoneNumber] = mapped_column(unique=True)
    birth_day: Mapped[datetime.date] = mapped_column()
    password: Mapped[HashedPassword] = mapped_column(nullable=False)
