"""
Configuration settings and environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Directory Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
TEMP_AUDIO_DIR = DATA_DIR / "audio"

# Database Configuration
DATABASE_PATH = DATA_DIR / "jobs.json"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Note: No OpenAI API key needed - using local Whisper + Ollama