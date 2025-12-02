"""Configuration for NCI evaluation framework."""

import os
from pathlib import Path

# Evaluation framework configuration
class EvalConfig:
    """Configuration for evaluation framework."""

    # Base paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    EVAL_DATASETS_DIR = DATA_DIR / "eval_datasets"
    EVAL_OUTPUT_DIR = PROJECT_ROOT / "eval_output"

    # Default threshold for binary classification (separates credible from manipulative)
    DEFAULT_THRESHOLD = 6

    # Number of samples to process per batch
    BATCH_SIZE = 10

    # Risk level thresholds
    RISK_LEVEL_THRESHOLDS = {
        "LOW": (0, 5),
        "MODERATE": (6, 10),
        "HIGH": (11, 15),
        "CRITICAL": (16, 20),
    }

    # Fact-checking data sources configuration
    SNOPES_API_URL = "https://www.snopes.com/api/v1"
    POLITIFACT_API_URL = "https://www.politifact.com/api/v2"

    # Visualization settings
    PLOT_DPI = 100
    PLOT_FIGSIZE = (12, 8)
    PLOT_STYLE = "seaborn-v0_8-darkgrid"

    # Report generation
    REPORT_TITLE = "NCI Scoring System Evaluation Report"
    INCLUDE_CASE_STUDIES = True
    MAX_CASE_STUDIES = 5

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.EVAL_DATASETS_DIR.mkdir(parents=True, exist_ok=True)
        cls.EVAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (cls.EVAL_DATASETS_DIR / "manipulative").mkdir(parents=True, exist_ok=True)
        (cls.EVAL_DATASETS_DIR / "credible").mkdir(parents=True, exist_ok=True)

