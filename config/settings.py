import os
from pydantic import Field
from pydantic_settings import BaseSettings

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

