from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase (get these from your Supabase project Settings → API)
    supabase_url: str = ""
    supabase_key: str = ""  # Use the "service_role" key (not anon)
    supabase_storage_bucket: str = "ddq-documents"

    # Database (get from Supabase Settings → Database → Connection string)
    database_url: str = ""

    # Claude API
    anthropic_api_key: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env"}


settings = Settings()
