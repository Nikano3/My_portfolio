from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_DB: str
    JWT_SECRET: str
    JWT_LIFETIME: int  # лучше int, если это число в секундах

    class Config:
        env_file = os.path.abspath("F:/Project_python/.env")


settings = Settings()
