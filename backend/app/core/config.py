from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "GreenLens"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Set DATABASE_URL to a PostgreSQL URL in backend/.env.
    # SQLite remains the development fallback for existing installations.
    DATABASE_URL: str = "sqlite:///./greenlens.db"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    ARTIFICIAL_ANALYSIS_API_KEY: str | None = None
    DEFAULT_PROVIDER: str = "OpenRouter"
    DEFAULT_MODEL: str = "openai/gpt-oss-20b:free"
    LOG_LEVEL: str = "INFO"

    FRONTEND_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,https://green-lens-gilt.vercel.app"

    SESSION_COOKIE_NAME: str = "greenlens_session"
    SESSION_SECRET: str = "Hwut8mfBOgzmN2jPVaQd4cDlBmSp_NwcjP5I0A88RKUiaF4silAZdtW7iz_nJITU"
    SESSION_MAX_AGE_DAYS: int = 30

    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    # GOOGLE_CLIENT_ID: str = ""
    # SESSION_COOKIE_NAME: str = "greenlens_session"
    # SESSION_SECRET: str = "change-this-development-secret-before-deployment"
    # SESSION_MAX_AGE_DAYS: int = 30
    # COOKIE_SECURE: bool = False
    # COOKIE_SAMESITE: str = "lax"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
