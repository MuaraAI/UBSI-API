from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8300
    REDIS_URL: str = "redis://127.0.0.1:6379/2"

    API_KEY: str = ""
    ALLOWED_ORIGINS: str = "*"
    TRUSTED_PROXIES: str = "127.0.0.1"
    ROOT_PATH: str = ""

    # Supabase Vault & Member Key Configuration (Opsional - Cloud Mode)
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    VAULT_ENCRYPTION_KEY: str = ""

    # Scraper Proxy Configuration (Opsional - Single Proxy / Rotating Pool)
    SCRAPER_PROXY: str = ""
    SCRAPER_PROXY_POOL: str = ""

    STUDENTV2_NIM: str = ""
    STUDENTV2_PASS: str = ""
    ELEARNING_NIM: str = ""
    ELEARNING_PASS: str = ""

    TTL_DEFAULT: int = 60
    TTL_SCHEDULE: int = 7200
    TTL_GRADES: int = 1800
    TTL_ASSIGNMENTS: int = 600
    TTL_NEWS: int = 900
    TTL_LIBRARY: int = 3600

    NEWS_WEBHOOK_URL: str = ""
    NEWS_WEBHOOK_INTERVAL: int = 600  # seconds (10 min)
    DISCORD_WEBHOOK_URL: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
