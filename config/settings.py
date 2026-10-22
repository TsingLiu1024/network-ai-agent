"""Validated configuration shared by every component."""

from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
        case_sensitive=True,
    )
    MODEL_PROVIDER: Literal["ollama", "deepseek", "openai", "demo"] = Field(
        default="ollama", validation_alias=AliasChoices("MODEL_PROVIDER", "LLM_PROVIDER")
    )
    OLLAMA_URL: str = Field(
        default="http://localhost:11434", validation_alias=AliasChoices("OLLAMA_URL", "OLLAMA_HOST")
    )
    OLLAMA_MODEL: str = "deepseek-r1:7b"
    DEEPSEEK_API_KEY: SecretStr | None = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    OPENAI_API_KEY: SecretStr | None = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    API_KEY: SecretStr | None = None
    ENABLE_RAG: bool = True
    VECTOR_DB_PATH: Path = BASE_DIR / "vector_db"
    KNOWLEDGE_PATH: Path = BASE_DIR / "knowledge"
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_LOCAL_ONLY: bool = True
    RAG_TOP_K: int = Field(default=3, ge=1, le=10)
    RAG_MIN_SCORE: float = Field(default=0.3, ge=-1, le=1)
    RAG_MAX_FILE_BYTES: int = Field(default=2_000_000, ge=1, le=10_000_000)
    RAG_MAX_TOTAL_BYTES: int = Field(default=10_000_000, ge=1, le=50_000_000)
    RAG_LOCK_TIMEOUT: float = Field(default=10, gt=0, le=60)
    ENABLE_TOKEN_OPTIMIZER: bool = True
    MAX_CONTEXT_LENGTH: int = Field(default=12000, ge=100, le=100000)
    MAX_LLM_OUTPUT_CHARS: int = Field(default=8000, ge=100, le=50000)
    LLM_TIMEOUT: float = Field(default=30, gt=0, le=120)
    DIAGNOSIS_TIMEOUT: float = Field(default=75, gt=0, le=300)
    TOOL_TIMEOUT: float = Field(default=5, gt=0, le=20)
    MAX_CONCURRENT_DIAGNOSES: int = Field(default=2, ge=1, le=16)
    COLLECT_LOCAL_EVIDENCE: bool = False
    ALLOW_CLOUD_LOG_UPLOAD: bool = False

    @field_validator("MODEL_PROVIDER", mode="before")
    @classmethod
    def normalize_provider(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("OLLAMA_URL", "OPENAI_BASE_URL", "DEEPSEEK_BASE_URL")
    @classmethod
    def validate_endpoint(cls, value):
        from urllib.parse import urlsplit

        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Endpoint must be HTTP(S) without credentials, query or fragment")
        return value.rstrip("/")

    @field_validator("OLLAMA_MODEL", "OPENAI_MODEL", "DEEPSEEK_MODEL", "EMBEDDING_MODEL")
    @classmethod
    def nonempty_model(cls, value):
        if not value.strip():
            raise ValueError("Model name cannot be empty")
        return value.strip()

    @field_validator("VECTOR_DB_PATH", "KNOWLEDGE_PATH")
    @classmethod
    def absolute_path(cls, value):
        return value.resolve() if value.is_absolute() else (BASE_DIR / value).resolve()


settings = Settings()
