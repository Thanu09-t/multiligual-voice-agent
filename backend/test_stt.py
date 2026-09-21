import asyncio
import httpx
import os
import io
import wave
import struct
from dotenv import load_dotenv


load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")

def generate_silent_wav() -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        # 1 second of 440Hz tone
        for i in range(16000):
            sample = int(32767 * 0.1 * (1 if (i // 20) % 2 == 0 else -1))
            wav_file.writeframes(struct.pack('<h', sample))
    return buf.getvalue()

async def test_stt():
    print(f"Testing Groq Whisper STT with key {groq_key[:10]}...")
    wav_data = generate_silent_wav()
    async with httpx.AsyncClient(timeout=15.0) as client:
        for model in ["whisper-large-v3-turbo", "whisper-large-v3"]:
            try:
                files = {
                    "file": ("audio.wav", wav_data, "audio/wav"),
                    "model": (None, model),
                }
                headers = {"Authorization": f"Bearer {groq_key}"}
                resp = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers=headers,
                    files=files
                )
                print(f"STT Model '{model}' status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"  >>> SUCCESS: text='{resp.json().get('text')}'")
                else:
                    print(f"  Error: {resp.text}")
            except Exception as e:
                print(f"  Exception with {model}: {e}")

if __name__ == "__main__":
    asyncio.run(test_stt())
