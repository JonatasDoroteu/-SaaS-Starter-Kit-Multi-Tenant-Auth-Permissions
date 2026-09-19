from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SaaS Starter"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    secret_key: str
    algorithm: str = "HS256"
    access_token_ttl_minutes: int = 60
    refresh_token_ttl_days: int = 7
    database_url: str = "sqlite+aiosqlite:///./saas_starter.db"
    notification_service_url: str = "http://localhost:3000"
    notification_service_key: str = "dev-service-key-change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
