from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "GreenLens"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./greenlens.db"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    DEFAULT_PROVIDER: str = "OpenRouter"
    # DEFAULT_MODEL: str = "google/gemma-4-31b-it:free"
    DEFAULT_MODEL: str = "openai/gpt-oss-20b:free"

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()