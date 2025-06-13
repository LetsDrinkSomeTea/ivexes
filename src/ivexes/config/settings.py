import os
from ivexes.config.components import banner
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv(verbose=True)
load_dotenv(verbose=True, dotenv_path=".secrets.env")

class Settings(BaseSettings):
    """
    Application settings using Pydantic.
    Environment variables take precedence over values defined here.
    """
    # OpenAI API settings
    openai_api_key: str = Field(default_factory=lambda: os.environ.get("OPENAI_API_KEY", ""))
    brave_search_api_key: str = Field(default_factory=lambda: os.environ.get("BRAVE_SEARCH_API_KEY", ""))

    # gets used
    llm_api_key: str = Field(default_factory=lambda: os.environ.get("LLM_API_KEY", os.environ.get("OPENAI_API_KEY", "")))
    llm_base_url: str = Field(default_factory=lambda: os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"))

    # Agent settings
    model: str = Field(default_factory=lambda: os.environ.get("MODEL", "openai/gpt-4o-mini"))
    temperature: float = Field(default_factory=lambda: float(os.environ.get("TEMPERATURE", "0.3")))
    max_turns: int = Field(default_factory=lambda: int(os.environ.get("MAX_TURNS", "10")))

    # Logging
    log_level: str = Field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))
    trace_name: str = Field(default_factory=lambda: os.environ.get("TRACE_NAME", "ivexes").lower())

    # Sandbox settings
    setup_archive: str = Field(default_factory=lambda: os.environ.get("SETUP_ARCHIVE", ""))

    # Codebase settings
    codebase_path: str | None = Field(default_factory=lambda: os.environ.get("CODEBASE_PATH", None))
    vulnerable_folder: str | None = Field(default_factory=lambda: os.environ.get("VULNERABLE_CODEBASE_FOLDER", None))
    patched_folder: str | None = Field(default_factory=lambda: os.environ.get("PATCHED_CODEBASE_FOLDER", None))

    # Embedding settings
    embedding_model: str = Field(default_factory=lambda: os.environ.get("EMBEDDING_MODEL", "builtin"))
    embedding_provider: str = Field(default_factory=lambda: os.environ.get("EMBEDDING_PROVIDER", "builtin"))


settings = Settings()
print(banner(
    model=settings.model,
    temperature=settings.temperature,
    max_turns=settings.max_turns,
    program_name=settings.trace_name,
))
