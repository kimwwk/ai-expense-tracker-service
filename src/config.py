"""
Configuration management using pydantic-settings.
Loads configuration from environment variables and .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database configuration
    database_url: str

    # Application environment
    environment: str = "development"

    # Logging configuration
    log_level: str = "INFO"

    # Database connection pool configuration
    db_pool_size: int = 20
    db_max_overflow: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
