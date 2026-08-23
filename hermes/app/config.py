import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file manually if exists to guarantee environment is loaded
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

class Settings(BaseSettings):
    # Supabase credentials
    SUPABASE_URL: str = "https://placeholder-project.supabase.co"
    SUPABASE_SERVICE_ROLE_KEY: str = "placeholder-key"

    # API Keys for LLM Providers
    ANTHROPIC_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    NVIDIA_API_KEY: str | None = None

    # AI Provider Routing (anthropic, groq, gemini, nvidia)
    PRIMARY_PROVIDER: str = "anthropic"

    # Security Config
    HERMES_API_KEY: str = "hermes-default-secret-key"
    ALLOWED_ORIGINS: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
