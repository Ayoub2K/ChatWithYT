"""
LLM operations for summary generation and Q&A using Ollama.
"""
import requests
import logging

logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


def generate_summary(transcript: str) -> str:
    """
    Generate a summary of the transcript using local Ollama LLM.
    Summary must be based strictly on transcript content.
    """
    prompt = f"""You are a helpful assistant that summarizes video transcripts.
Create a clear, concise summary that captures the main points and key takeaways.
Base your summary ONLY on the transcript provided. Do not add external information.

Transcript:
{transcript}

Please provide a comprehensive summary that covers the main topics and key points discussed."""
    
    try:
        logger.info("Generating summary with Ollama...")
        
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                }
            }
        )
        response.raise_for_status()
        
        summary = response.json()["response"]
        logger.info(f"Summary generated. Length: {len(summary)} characters")
        
        return summary
    
    except Exception as e:
        raise Exception(f"Summary generation failed: {str(e)}")


def answer_question(transcript: str, question: str) -> str:
    """
    Answer a question based strictly on the transcript using local Ollama LLM.
    Will not hallucinate or provide information beyond the transcript.
    """
    # Chunk transcript if it's very long (to fit context window)
    chunked_transcript = chunk_transcript(transcript, max_chars=12000)
    
    prompt = f"""You are a helpful assistant that answers questions about video transcripts.

CRITICAL RULES:
1. Answer questions ONLY based on the transcript provided
2. If the answer is not in the transcript, respond with "Not found in this video"
3. Do not use external knowledge or make assumptions
4. Quote relevant parts of the transcript when appropriate
5. Be concise and accurate

Transcript:
{chunked_transcript}

Question: {question}

Answer based ONLY on the transcript above. If the information is not in the transcript, say "Not found in this video"."""
    
    try:
        logger.info(f"Answering question with Ollama: {question}")
        
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,  # Use 0 for most deterministic answers
                }
            }
        )
        response.raise_for_status()
        
        answer = response.json()["response"]
        logger.info(f"Answer generated. Length: {len(answer)} characters")
        
        return answer
    
    except Exception as e:
        raise Exception(f"Question answering failed: {str(e)}")


def chunk_transcript(transcript: str, max_chars: int = 12000) -> str:
    """
    Chunk transcript if it exceeds max_chars.
    For simplicity, just truncate with a note.
    In production, you'd implement smarter chunking with semantic search.
    """
    if len(transcript) <= max_chars:
        return transcript
    
    # Truncate and add note
    truncated = transcript[:max_chars]
    return f"{truncated}\n\n[Note: Transcript truncated for length. Full transcript available.]"