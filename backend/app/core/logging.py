import json
import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger("nova.observability")


class PipelineLatencyTracker:
    """
    Tracks microsecond-level timestamps across every stage
    of the real-time voice pipeline.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"sess_{int(time.time() * 1000)}"
        self.timestamps: Dict[str, float] = {}
        self.record("session_started")

    def record(self, stage_name: str) -> float:
        now = time.time()
        self.timestamps[stage_name] = now
        return now

    def calculate_metrics(self) -> Dict[str, Any]:
        t = self.timestamps

        stt_latency = None
        if "transcription_started" in t and "transcription_completed" in t:
            stt_latency = round((t["transcription_completed"] - t["transcription_started"]) * 1000, 2)

        llm_latency = None
        if "agent_started" in t and "response_completed" in t:
            llm_latency = round((t["response_completed"] - t["agent_started"]) * 1000, 2)

        first_token_latency = None
        if "agent_started" in t and "first_token" in t:
            first_token_latency = round((t["first_token"] - t["agent_started"]) * 1000, 2)

        tts_latency = None
        if "tts_started" in t and "first_audio" in t:
            tts_latency = round((t["first_audio"] - t["tts_started"]) * 1000, 2)

        total_latency = None
        if "audio_received" in t and "first_audio" in t:
            total_latency = round((t["first_audio"] - t["audio_received"]) * 1000, 2)

        metrics = {
            "session_id": self.session_id,
            "stt_latency_ms": stt_latency,
            "llm_latency_ms": llm_latency,
            "time_to_first_token_ms": first_token_latency,
            "time_to_first_audio_ms": tts_latency,
            "total_turnaround_ms": total_latency,
        }

        logger.info(f"Pipeline Metrics: {json.dumps(metrics)}")
        return metrics
