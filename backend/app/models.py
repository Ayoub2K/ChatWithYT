from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Job(BaseModel):
    job_id: str
    url: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    error: Optional[str] = None
    access_links: List[str] = []
