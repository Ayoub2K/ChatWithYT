"""
Background worker for processing YouTube videos.
"""
import logging
import os
from pathlib import Path
import yt_dlp

from app.models import JobStatus
from app.speech import transcribe_audio
from app.llm import generate_summary
from app.config import TEMP_AUDIO_DIR

logger = logging.getLogger(__name__)


def process_video(job_id: str, url: str, db):
    """
    Complete video processing pipeline:
    1. Download audio
    2. Transcribe to text
    3. Generate summary
    4. Clean up
    """
    logger.info(f"Starting processing for job {job_id}")
    audio_path = None
    
    try:
        # Update status to processing
        db.update_job_status(job_id, JobStatus.PROCESSING)
        
        # Step 1: Download audio
        logger.info(f"Downloading audio for job {job_id}")
        audio_path = download_audio(url, job_id)
        
        # Step 2: Transcribe audio
        logger.info(f"Transcribing audio for job {job_id}")
        transcript = transcribe_audio(audio_path)
        
        if not transcript or not transcript.strip():
            raise ValueError("Transcription resulted in empty text")
        
        # Store transcript immediately
        db.update_job(job_id, {"transcript": transcript})
        logger.info(f"Transcript saved for job {job_id}")
        
        # Step 3: Generate summary
        logger.info(f"Generating summary for job {job_id}")
        summary = generate_summary(transcript)
        
        # Update job with final results
        db.update_job_status(
            job_id,
            JobStatus.DONE,
            transcript=transcript,
            summary=summary
        )
        
        logger.info(f"Job {job_id} completed successfully")
    
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}", exc_info=True)
        db.update_job_status(
            job_id,
            JobStatus.FAILED,
            error=str(e)
        )
    
    finally:
        # Clean up temporary audio file
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                logger.info(f"Deleted temporary audio file: {audio_path}")
            except Exception as e:
                logger.warning(f"Failed to delete audio file {audio_path}: {e}")


def download_audio(url: str, job_id: str) -> str:
    """
    Download audio from YouTube video using yt-dlp.
    Returns path to downloaded audio file.
    """
    # Ensure temp directory exists
    temp_dir = Path(TEMP_AUDIO_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Output path for audio file
    output_path = temp_dir / f"{job_id}.mp3"
    
    # yt-dlp options for audio download
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': str(temp_dir / job_id),
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if not output_path.exists():
            raise FileNotFoundError(f"Audio file not created at {output_path}")
        
        return str(output_path)
    
    except Exception as e:
        raise Exception(f"Failed to download audio: {str(e)}")