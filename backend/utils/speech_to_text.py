import io
import requests
import os
def speech_to_text_bytes(audio_bytes: bytes) -> str:
    buf = io.BytesIO(audio_bytes)
    buf.name = "audio.webm"
    response = requests.post(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
        files={"file": ("audio.webm", buf, "audio/webm")},
        data={"model": "whisper-large-v3-turbo", "language": "en", "response_format": "text"},
    )
    return response.text.strip()
