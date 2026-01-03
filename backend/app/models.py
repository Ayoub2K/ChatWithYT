"""
Data models and status constants.
"""
from datetime import datetime
from typing import Optional, List


class JobStatus:
    """Job status constants."""
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class Job:
    """
    Canonical job object representing a YouTube video processing task.
    """
    def __init__(
        self,
        job_id: str,
        url: str,
        status: str = JobStatus.QUEUED,
        created_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        transcript: Optional[str] = None,
        summary: Optional[str] = None,
        error: Optional[str] = None,
        access_links: Optional[List[str]] = None
    ):
        self.job_id = job_id
        self.url = url
        self.status = status
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.completed_at = completed_at
        self.transcript = transcript
        self.summary = summary
        self.error = error
        self.access_links = access_links or []
    
    def to_dict(self) -> dict:
        """Convert job to dictionary."""
        return {
            "job_id": self.job_id,
            "url": self.url,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "transcript": self.transcript,
            "summary": self.summary,
            "error": self.error,
            "access_links": self.access_links
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Job':
        """Create job from dictionary."""
        return cls(
            job_id=data["job_id"],
            url=data["url"],
            status=data["status"],
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            transcript=data.get("transcript"),
            summary=data.get("summary"),
            error=data.get("error"),
            access_links=data.get("access_links", [])
        )