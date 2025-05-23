import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv(verbose=True)


class Settings(BaseSettings):
    """
    Application settings using Pydantic.
    Environment variables take precedence over values defined here.
    """
    # OpenAI API settings
    openai_api_key: str = Field(default_factory=lambda: os.environ.get("OPENAI_API_KEY", ""))
    brave_search_api_key: str = Field(default_factory=lambda: os.environ.get("BRAVE_SEARCH_API_KEY", ""))

    # claude-3-haiku-20240307
    # gpt-4o-mini
    model: str = "gpt-4.1-mini"
    temperature: float = 0.3

    log_level: str = Field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))

    # Sandbox settings
    executable_archive: str = Field(default_factory=lambda: os.environ.get("EXECUTABLE_ARCHIVE", ""))

    # Codebase settings
    vulnerable_codebase_path: str = Field(default_factory=lambda: os.environ.get("VULNERABLE_CODEBASE_PATH", ""))
    patched_codebase_path: str = Field(default_factory=lambda: os.environ.get("PATCHED_CODEBASE_PATH", ""))

    # Embedding settings
    embedding_model: str = Field(default_factory=lambda: os.environ.get("EMBEDDING_MODEL", "text-embedding-3-large"))
    embedding_provider: str = Field(default_factory=lambda: os.environ.get("EMBEDDING_PROVIDER", "openai"))


settings = Settings()
