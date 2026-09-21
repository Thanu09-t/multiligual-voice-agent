import asyncio
import io
import wave
import math
import struct
import httpx
from app.config import settings
from app.providers.stt import get_stt_provider

def make_test_wav():
    buf = io.BytesIO()
    sample_rate = 16000
    duration = 1.5
    num_samples = int(sample_rate * duration)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            val = int(math.sin(2 * math.pi * 440 * (i / sample_rate)) * 10000)
            frames.extend(struct.pack("<h", val))
        wf.writeframes(frames)
    return buf.getvalue()

async def main():
    print(f"STT Provider: {settings.STT_PROVIDER}")
    print(f"Has Groq Key: {bool(settings.GROQ_API_KEY)}")
    stt = get_stt_provider()
    print(f"STT instance: {type(stt).__name__}")
    
    wav_bytes = make_test_wav()
    print(f"Generated test wav: {len(wav_bytes)} bytes")
    try:
        res = await stt.transcribe(wav_bytes, mime_type="audio/wav")
        print(f"Transcription result: '{res}'")
    except Exception as e:
        print(f"STT Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
