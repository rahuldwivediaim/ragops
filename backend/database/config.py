from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    database_url: str = Field(..., alias="DATABASE_URL")

    pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=1800, alias="DB_POOL_RECYCLE")

    echo_sql: bool = Field(default=False, alias="DB_ECHO_SQL")


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """
    Returns a cached instance of database settings.
    """
    return DatabaseSettings()
