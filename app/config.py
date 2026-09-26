from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8300
    REDIS_URL: str = "redis://127.0.0.1:6379/2"

    API_KEY: str = ""
    ALLOWED_ORIGINS: str = "*"
    TRUSTED_PROXIES: str = "127.0.0.1"

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
