from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(".env")


class _Settings(BaseSettings):
    SECRET_KEY: str = Field(examples=["YOUR_SECRET_KEY"])
    ENVIRONMENT: Literal["prod", "dev"] = Field(default="prod", examples=["dev"])
    DATABASE_URL: str = Field(examples=["sqlite:///db.sqlite3"])
    JWT_TOKEN_LIFETIME_MINUTES: int = Field(default=15, examples=[15])
    JWT_REFRESH_LIFETIME_DAYS: int = Field(default=30, examples=[30])
    HOST: str = Field(default="0.0.0.0", examples=["0.0.0.0"])
    PORT: int = Field(default=8000, examples=["8000"])
    ADMIN_EMAIL: str = Field(examples=["admin@example.com"])
    ADMIN_PASSWORD: str = Field(examples=["admin_secret_password"])

    model_config = SettingsConfigDict(env_file=ENV_FILE)
