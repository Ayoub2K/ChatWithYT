"""
Speech-to-text conversion using OpenAI Whisper API.
"""
import os
from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file to text using OpenAI Whisper API.
    
    Args:
        audio_path: Path to audio file (mp3, mp4, wav, etc.)
    
    Returns:
        Transcribed text
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    try:
        with open(audio_path, "rb") as audio_file:
            # Use Whisper API for transcription
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        # The API returns text directly when response_format="text"
        return transcript
    
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")


def transcribe_audio_local(audio_path: str) -> str:
    """
    Alternative: Transcribe using local Whisper model.
    Uncomment and use this if you want to avoid API costs.
    Requires: pip install openai-whisper
    
    import whisper
    
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]
    """
    pass