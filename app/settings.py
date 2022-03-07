from pydantic import BaseSettings
from typing import List

from pydantic.fields import Field


class Settings(BaseSettings):
    ENVIRONMENT: str = Field(default="local", env="ENVIRONMENT")

    # CORS related settings
    CORS_ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="CORS_ALLOWED_ORIGINS")
    ALLOWED_METHODS: List[str] = Field(default=["*"], env="ALLOWED_METHODS")
    ALLOWED_HEADERS: List[str] = Field(default=["*"], env="ALLOWED_HEADERS")
    AUTH_KEY: str = Field(default="", env="AUTH_KEY")
    MONGO_URI: str = Field(default="", env="MONGO_URI")

    PROJECT_NAME: str = Field(default="date-finder-be", env="PROJECT_NAME")
    PORT: str = Field(default="8080", env="PORT")


settings = Settings()
