from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase

from src.cutsom_types import HashedPassword, NationalID, PhoneNumber, StudnentID


class BaseModel(DeclarativeBase):
    type_annotation_map = {
        StudnentID: BigInteger(),
        NationalID: BigInteger(),
        PhoneNumber: BigInteger(),
        HashedPassword: String(),
    }
