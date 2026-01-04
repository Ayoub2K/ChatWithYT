"""
Speech-to-text conversion using local Whisper model.
"""
import os
import whisper
import logging
import torch
logger = logging.getLogger(__name__)

# Check for GPU availability
logger.info(f"PyTorch CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    logger.info(f"Whisper will use GPU: {torch.cuda.get_device_name(0)}")
else:
    logger.info("Whisper will use CPU")



# Load Whisper model once (cached)
# Options: tiny, base, small, medium, large
model = whisper.load_model("large")

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