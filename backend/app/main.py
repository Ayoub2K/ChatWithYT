"""
FastAPI application for YouTube transcript and Q&A backend.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging

from app.db import DatabaseManager
from app.worker import process_video
from app.utils import normalize_url, generate_job_id, generate_access_link
from app.models import JobStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="YouTube Transcript API")
db = DatabaseManager()


class SubmitJobRequest(BaseModel):
    url: str
    whisper_model: str = "base"  # default to base


class SubmitJobResponse(BaseModel):
    job_id: str
    status: str
    access_link: str


class StatusResponse(BaseModel):
    status: str


class ResultResponse(BaseModel):
    status: str
    transcript: Optional[str] = None
    summary: Optional[str] = None
    error: Optional[str] = None


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@app.post("/jobs", response_model=SubmitJobResponse)
async def submit_job(request: SubmitJobRequest, background_tasks: BackgroundTasks):
    """
    Submit a YouTube URL for processing.
    Deduplicates by canonical job_id.
    Always generates a new access_link.
    """
    try:
        # Normalize URL and generate canonical job_id
        normalized_url = normalize_url(request.url)
        job_id = generate_job_id(normalized_url)
        
        # Check if job already exists
        existing_job = db.get_job(job_id)
        
        # Generate new access link
        access_link = generate_access_link()
        
        if existing_job:
            # Reuse existing job, add new access link
            db.add_access_link(job_id, access_link)
            logger.info(f"Reusing existing job {job_id} with new access link")
            
            return SubmitJobResponse(
                job_id=job_id,
                status=existing_job["status"],
                access_link=access_link
            )
        else:
            # Create new job
            job = db.create_job(job_id, normalized_url, access_link)
            logger.info(f"Created new job {job_id}")
            
            # Start background processing
            background_tasks.add_task(process_video, job_id, normalized_url, db)
            
            return SubmitJobResponse(
                job_id=job_id,
                status=job["status"],
                access_link=access_link
            )
    
    except Exception as e:
        logger.error(f"Error submitting job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{access_link}/status", response_model=StatusResponse)
async def get_job_status(access_link: str):
    """
    Check the status of a job using its access link.
    """
    job = db.get_job_by_access_link(access_link)
    
    if not job:
        raise HTTPException(status_code=404, detail="Access link not found")
    
    return StatusResponse(status=job["status"])


@app.get("/jobs/{access_link}/result", response_model=ResultResponse)
async def get_job_result(access_link: str):
    """
    Get the result of a completed job.
    Returns status only if job is not done.
    """
    job = db.get_job_by_access_link(access_link)
    
    if not job:
        raise HTTPException(status_code=404, detail="Access link not found")
    
    if job["status"] != JobStatus.DONE:
        return ResultResponse(
            status=job["status"],
            error=job.get("error")
        )
    
    return ResultResponse(
        status=job["status"],
        transcript=job["transcript"],
        summary=job["summary"]
    )


@app.post("/jobs/{access_link}/chat", response_model=ChatResponse)
async def chat_with_transcript(access_link: str, request: ChatRequest):
    """
    Answer questions based strictly on the transcript.
    """
    from app.llm import answer_question
    
    job = db.get_job_by_access_link(access_link)
    
    if not job:
        raise HTTPException(status_code=404, detail="Access link not found")
    
    if job["status"] != JobStatus.DONE:
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    if not job["transcript"]:
        raise HTTPException(status_code=400, detail="No transcript available")
    
    try:
        answer = answer_question(job["transcript"], request.question)
        return ChatResponse(answer=answer)
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "YouTube Transcript API"}