from pathlib import Path
from typing import List, Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Entorno
    APP_ENV: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str = "America/Argentina/Buenos_Aires"
    REQUEST_TIMEOUT_SECONDS: int = 60

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(default="", description="Token del bot de Telegram")
    TELEGRAM_ALLOWED_USER_IDS: str = Field(default="", description="IDs de usuarios permitidos separados por coma")
    TELEGRAM_ALLOWED_CHAT_IDS: str = Field(default="", description="IDs de chats permitidos separados por coma")
    TELEGRAM_USE_WEBHOOK: bool = False

    # LLM
    DEFAULT_LLM_PROVIDER: Literal["gemini", "hermes", "anthropic"] = "gemini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Hermes (endpoint compatible con OpenAI / Ollama / vLLM / etc.)
    HERMES_API_BASE_URL: str = "http://localhost:11434/v1"
    HERMES_API_KEY: str = "none"
    HERMES_MODEL: str = "hermes-3-llama-3.1-8b"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-7-sonnet-20250219"

    # Persistencia
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/jarvis.db"

    # Seguridad
    ENCRYPTION_KEY: str = ""
    RATE_LIMIT_PER_USER: int = 20

    @property
    def allowed_users(self) -> List[int]:
        if not self.TELEGRAM_ALLOWED_USER_IDS.strip():
            return []
        return [int(uid.strip()) for uid in self.TELEGRAM_ALLOWED_USER_IDS.split(",") if uid.strip().isdigit()]

    @property
    def allowed_chats(self) -> List[int]:
        if not self.TELEGRAM_ALLOWED_CHAT_IDS.strip():
            return []
        return [int(cid.strip()) for cid in self.TELEGRAM_ALLOWED_CHAT_IDS.split(",") if cid.strip().lstrip("-").isdigit()]


settings = Settings()
