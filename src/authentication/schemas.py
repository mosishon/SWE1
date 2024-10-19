from pydantic import BaseModel, EmailStr

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


class ForgotPasswordData(BaseModel):
    email: EmailStr


class ResetForegetPasswordData(BaseModel):
    secret_token: str
    new_password: HashedPassword
    confirm_password: HashedPassword


class ResetPasswordOut(BaseModel):
    success: bool
    status_code: int
    message: str
