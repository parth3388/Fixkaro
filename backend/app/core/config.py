"""Application configuration, loaded from environment variables (.env in development)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "FIX-KAR Booking API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # PostgreSQL connection string, e.g.
    # postgresql+psycopg2://fixkar:password@localhost:5432/fixkar
    DATABASE_URL: str = "postgresql+psycopg2://fixkar:fixkar@localhost:5432/fixkar"

    # Comma-separated list of allowed browser origins for CORS.
    CORS_ORIGINS: str = "http://127.0.0.1:5500,http://localhost:5500"

    # Reserved for future signed tokens (e.g. admin auth). Not used by the
    # current anonymous-booking flow.
    SECRET_KEY: str = "change-me-in-production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
