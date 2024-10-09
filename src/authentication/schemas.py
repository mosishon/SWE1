from pydantic import BaseModel

from src.cutsom_types import HashedPassword, TimeStamp


# NOT FULL VERSION
class TokenData(BaseModel):
    user_id: int
    exp: TimeStamp
    force_exp: bool = False


class Token(BaseModel):
    token: str


class LoginData(BaseModel):
    username: str
    password: HashedPassword
