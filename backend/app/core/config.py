"""
Configuration file for environment variables and settings.
"""
from pathlib import Path
from typing import Dict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic v2 settings config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "AI Control Tower"
    ENV: str = "dev"

    # Base directory for safe data files (Data OS)
    DATA_BASE_DIR: str = str(
        Path(__file__).resolve().parent.parent.parent / "data"
    )

    # Logical dataset names → file names
    CSV_DATASETS: Dict[str, str] = {
        "customers": "customers.csv",
        "transactions": "transactions.csv",
        "logs": "logs.csv",
    }


settings = Settings()
