"""
Speech-to-text conversion using local Whisper model.
"""
import os
import whisper
import logging

logger = logging.getLogger(__name__)

# Cache for loaded models
_model_cache = {}


def get_model(model_name: str):
    """
    Get or load a Whisper model with caching.
    
    Args:
        model_name: One of "small", "base", "large"
    """
    # Map user-friendly names to actual Whisper model names
    model_map = {
        "small": "tiny",      # Fast for long videos
        "base": "base",       # Balanced (default)
        "large": "large"      # Best quality
    }
    
    actual_model = model_map.get(model_name, "base")
    
    if actual_model not in _model_cache:
        logger.info(f"Loading Whisper model: {actual_model}")
        _model_cache[actual_model] = whisper.load_model(actual_model)
    
    return _model_cache[actual_model]


def transcribe_audio(audio_path: str, model_name: str = "base") -> str:
    """
    Transcribe audio file to text using local Whisper model.
    
    Args:
        audio_path: Path to audio file (mp3, mp4, wav, etc.)
        model_name: One of "small", "base", "large"
    
    Returns:
        Transcribed text
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    try:
        logger.info(f"Transcribing audio with Whisper model '{model_name}': {audio_path}")
        
        model = get_model(model_name)
        result = model.transcribe(audio_path)
        
        transcript = result["text"]
        logger.info(f"Transcription completed. Length: {len(transcript)} characters")
        
        return transcript
    
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")