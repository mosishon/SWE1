from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class Settings(BaseSettings):
    SECRET: str = Field()
    FORGET_PASSWORD_SECRET: str
    FORGET_PASSWORD_LINK_EXPIRE_MINUTES: int
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    FORGOT_PASSWORD_URL: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool
    FRONTEND_DOMAIN: str
    model_config = SettingsConfigDict(env_file=".env")


config = Settings()  # type: ignore
