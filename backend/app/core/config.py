from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8", extra="ignore")

    postgres_db: str = "autogest"
    postgres_user: str = "autogest"
    postgres_password: str = "autogest_dev"

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@localhost:5432/{self.postgres_db}"

    jwt_secret: str = "autogest-dev-secret-cambia-esto-en-produccion"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    openai_api_key: str | None = None

    cors_origins: str = '["http://localhost:5173","http://localhost:8081"]'

    @property
    def cors_origins_list(self) -> list[str]:
        import json

        try:
            return json.loads(self.cors_origins)
        except Exception:
            return ["http://localhost:5173", "http://localhost:8081"]


settings = Settings()