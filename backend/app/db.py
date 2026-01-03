"""
Database manager using JSON file storage for simplicity.
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict
import threading
from datetime import datetime

from app.models import Job, JobStatus


class DatabaseManager:
    """
    Simple JSON-based database for job storage.
    Thread-safe operations using locks.
    """
    def __init__(self, db_path: str = "data/jobs.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self._initialize_db()
    
    def _initialize_db(self):
        """Create database file if it doesn't exist."""
        if not self.db_path.exists():
            self._write_db({})
    
    def _read_db(self) -> Dict:
        """Read database from disk."""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _write_db(self, data: Dict):
        """Write database to disk."""
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_job(self, job_id: str, url: str, access_link: str) -> Dict:
        """
        Create a new job with initial access link.
        """
        with self.lock:
            db = self._read_db()
            
            job = Job(
                job_id=job_id,
                url=url,
                status=JobStatus.QUEUED,
                access_links=[access_link]
            )
            
            db[job_id] = job.to_dict()
            self._write_db(db)
            
            return job.to_dict()
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by canonical job_id."""
        with self.lock:
            db = self._read_db()
            return db.get(job_id)
    
    def get_job_by_access_link(self, access_link: str) -> Optional[Dict]:
        """
        Find job by access link.
        Searches through all jobs to find matching access link.
        """
        with self.lock:
            db = self._read_db()
            for job_data in db.values():
                if access_link in job_data.get("access_links", []):
                    return job_data
            return None
    
    def add_access_link(self, job_id: str, access_link: str):
        """Add a new access link to an existing job."""
        with self.lock:
            db = self._read_db()
            
            if job_id in db:
                if access_link not in db[job_id]["access_links"]:
                    db[job_id]["access_links"].append(access_link)
                    self._write_db(db)
    
    def update_job_status(self, job_id: str, status: str, **kwargs):
        """
        Update job status and optional fields.
        kwargs can include: transcript, summary, error, completed_at
        """
        with self.lock:
            db = self._read_db()
            
            if job_id in db:
                db[job_id]["status"] = status
                
                # Update optional fields
                for key, value in kwargs.items():
                    if value is not None:
                        db[job_id][key] = value
                
                # Set completed_at if status is done or failed
                if status in [JobStatus.DONE, JobStatus.FAILED]:
                    db[job_id]["completed_at"] = datetime.utcnow().isoformat()
                
                self._write_db(db)
    
    def update_job(self, job_id: str, updates: Dict):
        """Update job with arbitrary fields."""
        with self.lock:
            db = self._read_db()
            
            if job_id in db:
                db[job_id].update(updates)
                self._write_db(db)