from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Central application configuration.

    Values are loaded from environment variables and .env file.
    Extra variables are forbidden to avoid misconfiguration.
    """

    # -------------------------------------------------
    # App
    # -------------------------------------------------
    PROJECT_NAME: str = "Group Fitness Booking API"
    API_V1_STR: str = "/api/v1"

    # -------------------------------------------------to j
    # Frontend
    # -------------------------------------------------
    FRONTEND_URL: str = Field(..., validation_alias="FRONTEND_URL")
    DEFAULT_LOCALE: str = Field("si", validation_alias="DEFAULT_LOCALE")

    # -------------------------------------------------
    # Security / Auth
    # -------------------------------------------------
    SECRET_KEY: str = Field(..., validation_alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # -------------------------------------------------
    # Database
    # -------------------------------------------------
    DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")
    TEST_DATABASE_URL: Optional[str] = Field(
        default=None,
        validation_alias="TEST_DATABASE_URL",
    )

    # -------------------------------------------------
    # Payments (Stripe)
    # -------------------------------------------------
    STRIPE_SECRET_KEY: str = Field(..., validation_alias="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(..., validation_alias="STRIPE_WEBHOOK_SECRET")

    # -------------------------------------------------
    # Email / SMTP
    # -------------------------------------------------
    SMTP_HOST: Optional[str] = Field(default=None, validation_alias="SMTP_HOST")
    SMTP_PORT: Optional[int] = Field(default=None, validation_alias="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, validation_alias="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, validation_alias="SMTP_PASSWORD")
    EMAIL_FROM: Optional[str] = Field(default=None, validation_alias="EMAIL_FROM")

    # -------------------------------------------------
    # AI / OpenAI
    # -------------------------------------------------
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        validation_alias="OPENAI_API_KEY",
    )

    # -------------------------------------------------
    # Pydantic settings behavior
    # -------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )


settings = Settings()