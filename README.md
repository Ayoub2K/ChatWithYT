# YouTube Transcript Backend

A FastAPI backend that downloads YouTube videos, transcribes them, generates summaries, and allows Q&A strictly grounded in the transcript.

## Features

- ✅ Canonical job deduplication per video
- ✅ Multiple users can access same job via different access links
- ✅ Asynchronous background processing
- ✅ No authentication system
- ✅ Shareable access links
- ✅ OpenAI Whisper for transcription
- ✅ GPT for summaries and Q&A

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install ffmpeg (Required by yt-dlp)

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

### 3. Set Environment Variables

Create a `.env` file or export variables:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
export OPENAI_MODEL="gpt-4o-mini"  # Optional, defaults to gpt-4o-mini
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Project Structure

```
backend/
├── app/
│   ├── main.py         # FastAPI routes
│   ├── models.py       # Job data model
│   ├── db.py          # JSON database manager
│   ├── worker.py      # Background processing
│   ├── utils.py       # URL normalization, hashing
│   ├── llm.py         # Summary and Q&A logic
│   ├── speech.py      # Whisper transcription
│   └── config.py      # Configuration
├── data/              # Database and temp files
│   ├── jobs.json      # Job storage
│   └── audio/         # Temporary audio files
└── requirements.txt   # Python dependencies
```

## API Endpoints

### 1. Submit Job
```bash
POST /jobs
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}

Response:
{
  "job_id": "abc123...",
  "status": "queued",
  "access_link": "xyz789..."
}
```

### 2. Check Status
```bash
GET /jobs/{access_link}/status

Response:
{
  "status": "processing"  # or "queued", "done", "failed"
}
```

### 3. Get Result
```bash
GET /jobs/{access_link}/result

Response (when done):
{
  "status": "done",
  "transcript": "Full transcript text...",
  "summary": "Summary of the video..."
}
```

### 4. Chat with Transcript
```bash
POST /jobs/{access_link}/chat
Content-Type: application/json

{
  "question": "What was discussed about AI?"
}

Response:
{
  "answer": "The video discussed..."
}
```

## Key Features Explained

### Canonical Job Deduplication
- Same YouTube URL always maps to same `job_id` (SHA256 hash)
- Video is processed only once
- Multiple users get different `access_link` tokens pointing to same job

### Access Links
- Each request generates a new unguessable access token
- No authentication needed
- Links are shareable

### Background Processing
- Jobs run asynchronously using FastAPI BackgroundTasks
- Status updates as job progresses: queued → processing → done/failed

### Grounded Q&A
- Chat answers are strictly based on transcript
- LLM instructed to say "Not found in this video" if answer not in transcript
- No hallucination or external knowledge

## Testing

```bash
# Submit a job
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Check status
curl http://localhost:8000/jobs/{access_link}/status

# Get result
curl http://localhost:8000/jobs/{access_link}/result

# Ask a question
curl -X POST http://localhost:8000/jobs/{access_link}/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this video about?"}'
```

## Notes

- Temporary audio files are automatically deleted after transcription
- Database is a simple JSON file for prototype simplicity
- No retry logic or rate limiting (prototype intentionally)
- English language only
- Transcripts are truncated to 12,000 chars for Q&A to fit context window

## Requirements

- Python 3.12
- OpenAI API key with access to Whisper and GPT models
- ffmpeg installed on system
- Internet connection for YouTube downloads