from pydantic_settings import BaseSettings, SettingsConfigDict

# Loads and validates environment variables from .env file using Pydantic

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: str
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"


settings = Settings()