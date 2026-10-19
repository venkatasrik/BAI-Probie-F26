"""
Configuration Module

This module handles configuration and environment variables for the chatbot.
We use Pydantic Settings to automatically load and validate environment variables
from a .env file, ensuring type safety and providing helpful error messages.

Key Concepts:
- Environment variables: Values stored outside your code (for security)
- Pydantic Settings: Automatic loading and validation of environment variables
- Type safety: Ensuring variables have the correct type before use
- Validation: Checking that values meet specific requirements

Best Practice:
- Environment variables (.env) should only contain SECRETS and deployment-specific values
- Application constants (like model names and prompts) belong in code, not .env
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from src.utils.filesystem import get_project_root

from src.chatbot.constants import ValidModel, DEFAULT_MODEL


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Pydantic Settings automatically:
    1. Reads from .env file
    2. Validates all fields match their type hints
    3. Uses default values when provided
    4. Raises clear errors if required fields are missing

    Attributes:
        OPENAI_API_KEY: Your OpenAI API key (required, kept secret)
        OPENAI_MODEL: Which GPT model to use (defaults to gpt-4o-mini)
    """

    # Required: Your OpenAI API key
    # This must be set in your .env file
    # This is a SECRET - never commit it to git!
    OPENAI_API_KEY: str

    # Optional: Override the default model
    # The default is defined in constants.py
    # Advanced users can override this in .env if needed
    OPENAI_MODEL: ValidModel = DEFAULT_MODEL

    # Configuration for Pydantic Settings
    # This tells it to look for a .env file
    model_config = SettingsConfigDict(
        env_file=get_project_root() / ".env",
    )


# Create a singleton instance of the Settings class to be used throughout the application
settings = Settings()
