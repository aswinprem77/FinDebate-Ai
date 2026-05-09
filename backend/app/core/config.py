from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "StockDebate.AI"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"
    jwt_secret: str = "change-me-before-deploy"
    jwt_expires_minutes: int = 60 * 24
    database_url: str | None = None
    redis_url: str | None = None
    evidence_cache_ttl_seconds: int = 15 * 60
    free_debates_per_hour: int = 5
    free_debates_per_day: int = 20
    pro_debates_per_hour: int = 30
    pro_warning_threshold_per_hour: int = 25
    model_timeout_seconds: int = 25
    judge_timeout_seconds: int = 10
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


settings = Settings()
