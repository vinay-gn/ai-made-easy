from functools import lru_cache
from pathlib import Path
from typing import get_args

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.models import TrackId

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    app_host: str = "127.0.0.1"
    app_port: int = 8001
    cors_origins: str = "http://localhost:5173"
    # Relative paths are resolved against the backend directory
    data_file: str = "app/data/roadmap.v2.json"
    # Comma-separated track ids exposed by the API; other tracks stay in the data file but are hidden
    enabled_tracks: str = "use"

    @field_validator("enabled_tracks")
    @classmethod
    def _check_enabled_tracks(cls, value: str) -> str:
        ids = [t.strip() for t in value.split(",") if t.strip()]
        if not ids:
            raise ValueError("ENABLED_TRACKS must list at least one track")
        if unknown := sorted(set(ids) - set(get_args(TrackId))):
            raise ValueError(f"ENABLED_TRACKS has unknown track ids: {unknown}")
        return value

    @property
    def enabled_track_list(self) -> list[str]:
        return [t.strip() for t in self.enabled_tracks.split(",") if t.strip()]

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
