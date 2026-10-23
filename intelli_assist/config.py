from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str = ""
    groq_chat_model: str = "openai/gpt-oss-120b"

    embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    knowledge_dir: str = str(ROOT_DIR / "data" / "knowledge")
    faiss_index_dir: str = str(ROOT_DIR / "data" / "index")
    sqlite_path: str = str(ROOT_DIR / "data" / "intelli_assist.db")

    retrieval_k: int = Field(default=5, ge=1, le=20)
    min_retrieval_score: float = Field(default=0.25, ge=0, le=1)

    max_history_turns: int = Field(default=12, ge=2, le=100)
    max_context_chars: int = Field(default=18000, ge=2000)
    summary_after_turns: int = Field(default=20, ge=4)

    llm_timeout_seconds: int = Field(default=30, ge=1)
    llm_max_retries: int = Field(default=2, ge=0, le=5)

    api_auth_enabled: bool = False
    api_bearer_token: str = ""

    cors_origins: str = "http://localhost:8501"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()