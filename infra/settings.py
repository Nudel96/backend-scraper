from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = Field(default="sqlite:///./app.db")
    redis_url: str = Field(default="redis://localhost:6379/0")
    environment: str = Field(default="dev")


settings = Settings()
