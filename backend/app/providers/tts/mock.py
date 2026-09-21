import math
import struct
import io
import wave
from typing import AsyncIterator, Optional
from app.providers.base import TTSProvider


def generate_synthetic_wav(text: str, duration_sec: float = 1.0, sample_rate: int = 22050) -> bytes:
    """
    Generate a clean PCM WAV audio stream with speech-like tones
    so any audio player or browser can play it directly without external keys.
    """
    num_samples = int(sample_rate * duration_sec)
    buffer = io.BytesIO()
    
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)       # Mono
        wav_file.setsampwidth(2)      # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Base frequency modulated by character codes
        base_freq = 280.0
        frames = bytearray()
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Harmonic blend mimicking pleasant voice tone
            char_idx = int(t * len(text) * 2) % max(1, len(text))
            char_factor = (ord(text[char_idx]) % 10) * 15.0
            freq = base_freq + char_factor
            
            # Envelope (attack & decay)
            envelope = min(1.0, t * 10) * max(0.0, 1.0 - (t / duration_sec))
            val = math.sin(2.0 * math.pi * freq * t) * 0.4
            val += math.sin(2.0 * math.pi * (freq * 1.5) * t) * 0.2
            sample_val = int(val * envelope * 32767.0)
            
            frames.extend(struct.pack("<h", max(-32768, min(32767, sample_val))))
            
        wav_file.writeframes(frames)
        
    return buffer.getvalue()


class MockTTSProvider(TTSProvider):
    """Synthetic audio provider generating genuine playable WAV audio."""

    async def synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        duration = min(3.0, max(0.6, len(text) * 0.05))
        return generate_synthetic_wav(text, duration_sec=duration)

    async def stream_synthesize(
        self, text: str, voice: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        audio_data = await self.synthesize(text, voice)
        # Yield in 4KB chunks
        chunk_size = 4096
        for i in range(0, len(audio_data), chunk_size):
            yield audio_data[i : i + chunk_size]
