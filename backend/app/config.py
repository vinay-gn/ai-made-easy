from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    app_host: str = "127.0.0.1"
    app_port: int = 8001
    cors_origins: str = "http://localhost:5173"
    # Relative paths are resolved against the backend directory
    data_file: str = "app/data/roadmap.v1.json"

    @property
    def data_file_path(self) -> Path:
        path = Path(self.data_file)
        return path if path.is_absolute() else BACKEND_DIR / path

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
