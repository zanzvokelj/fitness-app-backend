from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Group Training Booking API"
    API_V1_STR: str = "/api/v1"

    # Frontend
    FRONTEND_URL: str = Field(..., env="FRONTEND_URL")
    DEFAULT_LOCALE: str = Field("si", env="DEFAULT_LOCALE")

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    TEST_DATABASE_URL: str | None = Field(default=None, env="TEST_DATABASE_URL")

    # Stripe
    STRIPE_SECRET_KEY: str = Field(..., env="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(..., env="STRIPE_WEBHOOK_SECRET")

    # 🔽 EMAIL / SMTP (TO MANJKA)
    SMTP_HOST: str | None = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int | None = Field(default=None, env="SMTP_PORT")
    SMTP_USER: str | None = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: str | None = Field(default=None, env="SMTP_PASSWORD")
    EMAIL_FROM: str | None = Field(default=None, env="EMAIL_FROM")

    # 🔽 OPENAI (TO MANJKA)
    OPENAI_API_KEY: str | None = Field(default=None, env="OPENAI_API_KEY")

    # 🔽 RESEND (EMAIL API)
    RESEND_API_KEY: str | None = Field(default=None, env="RESEND_API_KEY")

    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()