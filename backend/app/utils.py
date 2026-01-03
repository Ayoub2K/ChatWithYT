"""
Utility functions for URL normalization, hashing, and token generation.
"""
import hashlib
import secrets
from urllib.parse import urlparse, parse_qs
import re


def normalize_url(url: str) -> str:
    """
    Normalize YouTube URL to canonical form.
    
    Handles:
    - youtu.be short links
    - youtube.com/watch?v=VIDEO_ID
    - youtube.com/v/VIDEO_ID
    - Removes unnecessary query parameters
    
    Returns canonical form: https://www.youtube.com/watch?v=VIDEO_ID
    """
    # Extract video ID from various YouTube URL formats
    video_id = extract_video_id(url)
    
    if not video_id:
        raise ValueError(f"Invalid YouTube URL: {url}")
    
    # Return canonical form
    return f"https://www.youtube.com/watch?v={video_id}"


def extract_video_id(url: str) -> str:
    """
    Extract video ID from YouTube URL.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    # Handle youtu.be short links
    if "youtu.be" in url:
        match = re.search(r"youtu\.be/([a-zA-Z0-9_-]+)", url)
        if match:
            return match.group(1)
    
    # Handle youtube.com URLs
    parsed = urlparse(url)
    
    # /watch?v=VIDEO_ID
    if parsed.path == "/watch":
        query_params = parse_qs(parsed.query)
        if "v" in query_params:
            return query_params["v"][0]
    
    # /v/VIDEO_ID or /embed/VIDEO_ID
    match = re.search(r"/(v|embed)/([a-zA-Z0-9_-]+)", parsed.path)
    if match:
        return match.group(2)
    
    return ""


def generate_job_id(normalized_url: str) -> str:
    """
    Generate canonical job_id from normalized URL using SHA256 hash.
    """
    return hashlib.sha256(normalized_url.encode()).hexdigest()


def generate_access_link() -> str:
    """
    Generate cryptographically secure random access link token.
    Uses 32 bytes = 256 bits of randomness.
    """
    return secrets.token_urlsafe(32)