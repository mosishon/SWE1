from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class Settings(BaseSettings):
    SECRET: str = Field()
    FORGET_PASSWORD_SECRET: str
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    HOST: str
    PORT: int
    FORGOT_PASSWORD_URL: str
    # MAIL_USERNAME: str
    # MAIL_PASSWORD: str
    # MAIL_FROM: str
    # MAIL_PORT: int
    # MAIL_SERVER: str
    # MAIL_STARTTLS: bool
    # MAIL_SSL_TLS: bool
    # USE_CREDENTIALS: bool
    # VALIDATE_CERTS: bool
    model_config = SettingsConfigDict(env_file=".env")


config = Settings()  # type: ignore
