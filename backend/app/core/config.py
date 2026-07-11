from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "DevHub AI"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    database_url: str = "postgresql+psycopg2://devhub:devhub@localhost:5432/devhub"

    secret_key: str = "change-me-to-a-long-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost"

    upload_dir: str = "uploads"
    max_upload_size_mb: int = 100
    
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    
    # Unified AI Platform Configs
    ai_provider: str = "gemini"
    ai_model: str = ""
    ai_api_key: str = ""
    ai_base_url: str = ""
    ai_timeout: float = 30.0
    ai_max_tokens: int = 2048
    ai_temperature: float = 0.7
    ai_stream: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
