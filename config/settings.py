import os
from config.components import banner
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

    # Agent settings
    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    max_turns: int = Field(default_factory=lambda: int(os.environ.get("MAX_TURNS", "10")))

    # Logging
    log_level: str = Field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))
    trace_name: str = Field(default_factory=lambda: os.environ.get("TRACE_NAME", "ivexes"))

    # Sandbox settings
    setup_archive: str = Field(default_factory=lambda: os.environ.get("SETUP_ARCHIVE", ""))

    # Codebase settings
    codebase_path: str = Field(default_factory=lambda: os.environ.get("CODEBASE_PATH", ""))
    vulnerable_folder: str = Field(default_factory=lambda: os.environ.get("VULNERABLE_CODEBASE_FOLDER", ""))
    patched_folder: str = Field(default_factory=lambda: os.environ.get("PATCHED_CODEBASE_FOLDER", ""))

    # Embedding settings
    embedding_model: str = Field(default_factory=lambda: os.environ.get("EMBEDDING_MODEL", "text-embedding-3-large"))
    embedding_provider: str = Field(default_factory=lambda: os.environ.get("EMBEDDING_PROVIDER", "openai"))


settings = Settings()
print(banner(
    model=settings.model,
    temperature=settings.temperature,
    max_turns=settings.max_turns,
))
