from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class Settings(BaseSettings):
    SECRET: str = Field()
    model_config = SettingsConfigDict(env_file=".env")


config = Settings()  # type: ignore
