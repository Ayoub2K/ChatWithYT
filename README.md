# ChatWithYT

Convert any video into searchable text with AI-powered summaries and Q&A. Runs 100% locally on your machine - no API costs, complete privacy.

## What It Does

1. **Paste a YT URL** → Downloads audio
2. **Transcribes with Whisper** → Converts speech to text (GPU-accelerated)
3. **Generates summary** → Creates AI summary with Ollama
4. **Ask questions** → Chat about the video content

## Quick Start

### Prerequisites
- Python 3.10+
- NVIDIA GPU (recommended) or CPU
- 10GB free disk space

### Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install ffmpeg
# Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
# Extract and copy ffmpeg.exe to the backend folder

# 3. Install Ollama
# Download from: https://ollama.com/download
# Then pull a model:
ollama pull llama3.2

# 4. (Optional) GPU acceleration for Whisper
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Run

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

API docs at: http://localhost:8000/docs

## Usage

### Submit a Video
```bash
POST http://localhost:8000/jobs
Body: {"url": "video url"}

Response: {
  "job_id": "...",
  "status": "queued",
  "access_link": "abc123..."
}
```

### Check Status
```bash
GET http://localhost:8000/jobs/{access_link}/status
```

### Get Result
```bash
GET http://localhost:8000/jobs/{access_link}/result
```

### Ask Questions
```bash
POST http://localhost:8000/jobs/{access_link}/chat
Body: {"question": "What is this video about?"}
```

## Performance

With RTX 4070 + Whisper Large model:
- **10-min video**: ~4-6 minutes total
- **Transcription**: ~3-5 minutes (GPU)
- **Summary**: ~10-30 seconds

## Tech Stack

- **Backend**: FastAPI + Python
- **Transcription**: OpenAI Whisper (local)
- **LLM**: Ollama (llama3.2)
- **Audio**: yt-dlp + ffmpeg
- **Storage**: JSON file database

## Troubleshooting

**"Module not found" error**: Make sure you're in the `backend` folder when running uvicorn

**"ffmpeg not found"**: Copy `ffmpeg.exe` to your `backend` folder

**Slow transcription**: Install PyTorch with CUDA for GPU acceleration

**Chat answers not good**: Upgrade Ollama model with `ollama pull llama3.1:8b`


## Disclaimer
This tool is for personal/educational use. Respect YouTube's Terms of Service 
and copyright laws. Don't download copyrighted content without permission.
