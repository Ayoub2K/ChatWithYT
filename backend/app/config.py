"""
Configuration settings and environment variables.
"""
import os
from pathlib import Path

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Use gpt-4o-mini for cost efficiency

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable must be set")

# Directory Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
TEMP_AUDIO_DIR = DATA_DIR / "audio"

# Database Configuration
DATABASE_PATH = DATA_DIR / "jobs.json"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)