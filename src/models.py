import datetime

from sqlalchemy import BigInteger, String
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


# TODO We need a base user and use it for all user types  (Student,Instructor,Admin , ...)


class User(BaseModel):
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    national_id: Mapped[NationalID] = mapped_column(index=True)
    email: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(index=True)
    phone_number: Mapped[PhoneNumber] = mapped_column()
    birth_day: Mapped[datetime.datetime] = mapped_column()
    password: Mapped[HashedPassword] = mapped_column()
