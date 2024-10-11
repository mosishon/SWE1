from pydantic import BaseModel

from src.cutsom_types import HashedPassword, TimeStamp


# NOT FULL VERSION
class TokenData(BaseModel):
    user_id: int
    exp: TimeStamp


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginData(BaseModel):
    username: str
    password: HashedPassword
