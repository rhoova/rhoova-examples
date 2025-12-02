"""Global configuration loaded from environment variables.

Attributes
----------
redis_url : str
    Redis connection URI.
sqlite_path : str
    File path for the SQLite database.
refresh_sec : int
    UI auto‑refresh interval in seconds.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from rhoova_folder.scenario import ScenarioAnalyzer
from rhoova_folder.portfolio import loadportfolio

class Settings(BaseSettings):
    """Application‑wide settings.

    Environment variables override the default values. All settings are
    validated at import time.
    """

    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    sqlite_path: str = Field("alert_log.db", env="SQLITE_PATH")
    refresh_sec: int = Field(5, env="REFRESH_SEC")
    ws_host: str = "localhost"
    ws_port: int = 8000
    telegram_token: str = ""  # Replace with your Telegram bot token
    telegram_chat_id: str = ""
    valuationdate: str ="2025-02-25"
    currency: str ="TRY"
    method: str ="total_present_value"
    portfolio: dict =loadportfolio(valuationdate,"TRY",method)


    class Config:
        env_file = ".env"


settings = Settings()


