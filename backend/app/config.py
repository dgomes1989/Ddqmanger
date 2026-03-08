from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://ddqmanager:ddqmanager@localhost:5432/ddqmanager"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket_name: str = "ddq-documents"
    anthropic_api_key: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env"}


settings = Settings()
