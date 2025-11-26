"""Configuration management for Deep Research Agent."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for managing API keys and settings."""

    # Minimax API Configuration
    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
    MINIMAX_BASE_URL = "https://api.minimax.io/anthropic"
    MINIMAX_MODEL = "MiniMax-M2"

    # OpenRouter API Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL = "minimax/minimax-m2"

    # Exa API Configuration
    EXA_API_KEY = os.getenv("EXA_API_KEY")
    EXA_BASE_URL = "https://api.exa.ai"
    EXA_HIGH_PRIORITY_RESULTS = int(os.getenv("EXA_HIGH_PRIORITY_RESULTS", "20"))
    EXA_NORMAL_PRIORITY_RESULTS = int(os.getenv("EXA_NORMAL_PRIORITY_RESULTS", "15"))
    EXA_SIMILAR_RESULTS = int(os.getenv("EXA_SIMILAR_RESULTS", "5"))

    # Debug Configuration
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # NCI (Narrative Credibility Index) Scoring Configuration
    NCI_SCORING_ENABLED = os.getenv("NCI_SCORING_ENABLED", "false").lower() == "true"
    NCI_SCORE_THRESHOLD = int(os.getenv("NCI_SCORE_THRESHOLD", "6"))
    NCI_TOP_N_SOURCES = int(os.getenv("NCI_TOP_N_SOURCES", "5"))

    @classmethod
    def validate(cls):
        """Validate that all required API keys are set."""
        missing = []

        if not cls.OPENROUTER_API_KEY:
            missing.append("OPENROUTER_API_KEY")
        if not cls.EXA_API_KEY:
            missing.append("EXA_API_KEY")

        if missing:
            raise ValueError(
                f"Missing required API keys: {', '.join(missing)}. "
                f"Please set them in your .env file."
            )

        return True
