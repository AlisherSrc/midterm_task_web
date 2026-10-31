"""Application configuration loaded from environment variables."""

import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Space Bounty Hunters REST API"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # PostgreSQL Database connection parameters
    postgres_user: str = "postgres"
    postgres_password: str = Field(default="postgres", repr=False)
    postgres_db: str = "space_bounty_hunters"
    db_host: str = "localhost"
    db_port: int = 5432

    # Direct database URL override (e.g. for sqlite test, or cloud postgres)
    database_url_override: str | None = Field(default=None, alias="DATABASE_URL")

    @property
    def database_url(self) -> str | URL:
        if self.database_url_override:
            return self.database_url_override
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.db_host,
            port=self.db_port,
            database=self.postgres_db,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
