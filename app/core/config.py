from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TicketFlow"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings() # type: ignore[call-arg]

