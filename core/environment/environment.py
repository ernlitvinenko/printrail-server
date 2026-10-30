from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

ENV_FILE = Path(".env")

class _Settings(BaseSettings):
    SECRET_KEY: str = Field(examples=["YOUR_SECRET_KEY"])
    DATABASE_URL: str = Field(examples=["sqlite:///db.sqlite3"])
    HOST: str = Field(default="0.0.0.0", examples=["0.0.0.0"])
    PORT: int = Field(default=8000, examples=["8000"])

    model_config = SettingsConfigDict(env_file=ENV_FILE)
