from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FactoryIQ Manufacturing Excellence Portal"
    database_url: str = "sqlite:///./factoryiq.db"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "factoryiq-docs"
    smtp_from: str = "no-reply@factoryiq.local"

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")


settings = Settings()
