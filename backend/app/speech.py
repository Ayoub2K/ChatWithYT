"""
Speech-to-text conversion using local Whisper model.
"""
import os
import whisper
import logging

logger = logging.getLogger(__name__)

# Load Whisper model once (cached)
# Options: tiny, base, small, medium, large
# base = good balance of speed/accuracy for prototypes
model = whisper.load_model("base")


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file to text using local Whisper model.
    
    Args:
        audio_path: Path to audio file (mp3, mp4, wav, etc.)
    
    Returns:
        Transcribed text
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    try:
        logger.info(f"Transcribing audio with local Whisper model: {audio_path}")
        
        # Transcribe using local Whisper
        result = model.transcribe(audio_path)
        
        transcript = result["text"]
        logger.info(f"Transcription completed. Length: {len(transcript)} characters")
        
        return transcript
    
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")