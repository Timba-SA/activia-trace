from functools import lru_cache

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    database_url: str = Field(..., description="PostgreSQL DSN con driver asyncpg")
    database_url_test: str = Field(default="", description="PostgreSQL DSN de test (opcional)")
    secret_key: str = Field(..., min_length=32, description="JWT signing key (min 32 chars)")
    encryption_key: str = Field(..., min_length=32, max_length=32, description="AES-256 key (exactly 32 chars)")
    access_token_expire_minutes: int = Field(default=15, ge=1, description="Access token TTL in minutes")

    refresh_token_expire_days: int = Field(default=7, ge=1, description="Refresh token TTL in days")
    rate_limit_max_requests: int = Field(default=5, ge=1, description="Max login attempts per window")
    rate_limit_window_seconds: int = Field(default=60, ge=1, description="Rate limit window in seconds")
    recovery_token_expire_minutes: int = Field(default=15, ge=1, description="Recovery token TTL in minutes")

    otel_service_name: str = Field(default="active-trace", description="OpenTelemetry service name")
    otel_exporter_otlp_endpoint: str | None = Field(default=None, description="OTLP exporter endpoint")
    otel_traces_sampler: str = Field(default="parentbased_always_on", description="OTel sampler")

    @field_validator("encryption_key")
    @classmethod
    def encryption_key_length(cls, v: str) -> str:
        if len(v) != 32:
            raise ValueError("encryption_key must be exactly 32 characters")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
