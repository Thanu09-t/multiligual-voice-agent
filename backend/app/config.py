import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "NOVA Voice Agent"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./nova.db"

    # Security
    JWT_SECRET: str = "super-secret-nova-development-key-change-in-production-32bytes"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Providers
    LLM_PROVIDER: str = "mock"
    LLM_MODEL: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    STT_PROVIDER: str = "mock"
    STT_API_KEY: str = ""

    TTS_PROVIDER: str = "mock"
    TTS_API_KEY: str = ""
    DEFAULT_VOICE: str = "en-US-JennyNeural"
    SPEECH_SPEED: float = 1.0

    # Tools
    WEATHER_API_KEY: str = ""
    SEARCH_API_KEY: str = ""
    SEARCH_PROVIDER: str = "duckduckgo"  # Options: tavily | serper | duckduckgo

    # Voice Activity Detection
    VAD_ENERGY_THRESHOLD: float = 0.010
    VAD_SILENCE_TIMEOUT_MS: int = 260

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
