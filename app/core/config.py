from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Group Training Booking API"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    TEST_DATABASE_URL: str | None = Field(default=None, env="TEST_DATABASE_URL")

    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()