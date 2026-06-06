import io
import edge_tts
import asyncio
from backend.config.voice import INTERVIEWER_VOICE
# ── TTS : edge-tts
async def _tts_async(text: str, voice: str) -> bytes:
    buf = io.BytesIO()
    communicate = edge_tts.Communicate(text, voice=voice, rate="-5%")
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    buf.seek(0)
    return buf.read()
 
 
def text_to_speech_bytes(text: str, voice: str = INTERVIEWER_VOICE) -> bytes:
    """Synchronous wrapper around the async edge-tts call."""
    return asyncio.run(_tts_async(text, voice))
 