
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    rate_limit_urls: int = Field(..., env="RATE_LIMIT_URLS")
    rate_limit_comps: int = Field(..., env="RATE_LIMIT_COMPS")
    workers: int = Field(..., env="WORKERS")
    categories: List[str] = Field(..., env="CATEGORIES")
    cities: List[str] = Field(..., env="CITIES")
    products: int = Field(..., env="PRODUCTS")
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
