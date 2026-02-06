"""
Application Configuration and Environment Settings.

This module manages environment variables and system-wide settings using Pydantic.
It handles:
- Timezone definitions for Moscow and Europe/Moscow.
- PostgreSQL database credentials and connection parameters.
- Deribit API URL configuration for engine.
- Automatic loading of the .env file from the project root.
"""
import os
from datetime import timezone, timedelta
from pathlib import Path
from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

local_zone = ZoneInfo('Europe/Moscow')
moscow_tz = timezone(timedelta(hours=3))

class Settings(BaseSettings):
    """
    Settings class to validate and store application environment variables.
    """
    POSTGRES_USER: Annotated[str, Field(min_length=3)]
    POSTGRES_PASSWORD: Annotated[str, Field(min_length=3)]
    POSTGRES_DB: Annotated[str, Field()]
    POSTGRES_HOST: Annotated[str, Field()]
    POSTGRES_PORT: Annotated[str, Field(min_length=3)]
    redis_host: str = "localhost"

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE_PATH", os.path.join(Path(__file__).parent.parent.parent, '.env')),
        extra='ignore'  # Игнорировать лишние переменные в .env
    )

    def get_db_url(self):
        database_url = 'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}'.format(
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB)
        return database_url

settings = Settings()

db_url = settings.get_db_url()

