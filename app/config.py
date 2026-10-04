import os

from dotenv import load_dotenv


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")


def validate_config() -> None:
    """Validate configuration required for live LLM execution."""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not configured. "
            "Add it to the .env file before running the live workflow."
        )

    if not MODEL_NAME:
        raise ValueError("MODEL_NAME must not be empty.")