import asyncio

import jwt
from passlib.context import CryptContext

from src.authentication.constants import ALGORITHM
from src.authentication.schemas import Token, TokenData
from src.config import config
from src.cutsom_types import HashedPassword

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw_password: str) -> HashedPassword:
    hashed = HashedPassword(pwd_context.hash(raw_password))
    return hashed


def verify_pwd(plain: str, hash: HashedPassword) -> bool:
    return pwd_context.verify(plain, hash)


def create_access_token(token_data: TokenData) -> Token:
    encoded = jwt.encode(token_data.model_dump(), config.SECRET, ALGORITHM)
    return Token(access_token=encoded)


async def to_async(fn, *args):
    return await asyncio.get_event_loop().run_in_executor(None, fn, *args)
