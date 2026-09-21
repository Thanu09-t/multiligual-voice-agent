# NOVA Architecture Documentation

## 1. Overview
NOVA is a multimodal, real-time AI voice agent designed with a voice-first operating interface. It integrates Voice Activity Detection (VAD), streaming Speech-to-Text (STT), a multi-step agent reasoning loop, tool execution with safety confirmation, semantic memory retrieval, document RAG, and streaming Text-to-Speech (TTS) with instant user barge-in (interruption).

## 2. Component Pipeline

```
[User Microphone]
        │
        ▼ (Web Audio API Analyser)
[Client-Side VAD Engine] ─── (Barge-in: cancels ongoing playback & server tasks)
        │
        ▼ (Binary PCM / Audio Chunks via WebSocket)
[FastAPI WebSocket Endpoint (/api/voice)]
        │
        ▼
[STT Provider (Whisper / Groq / Fallback)]
        │ (Streaming partial / final transcript)
        ▼
[Agent Orchestration Layer]
   ├── [Input Normalization & Intent Understanding]
   ├── [Memory Retrieval (Short-Term Window + Long-Term Facts)]
   ├── [RAG Retrieval (Indexed Document Chunks)]
   ├── [Tool Decision & Execution (Calculator, Weather, Web/File Search)]
   └── [Final Reasoning & Response Synthesis]
        │ (Display Text vs Spoken Text)
        ▼
[LLM Provider (OpenAI / Groq / Gemini / Offline-Mock)]
        │ (Streaming token deltas)
        ▼
[TTS Provider (Edge-TTS / Streaming / Audio Chunks)]
        │
        ▼ (Base64 Audio Chunks via WebSocket)
[Client Audio Playback Queue] ───► [Speaker]
```

## 3. State Management
The agent lifecycle transitions through strictly typed states:
- `IDLE`: Listening for activation or idle wait.
- `LISTENING`: User speech detected; receiving audio buffer.
- `THINKING`: Processing prompt, querying memory/RAG.
- `USING_TOOL`: Executing tool (calculator, weather, search).
- `GENERATING`: LLM streaming response tokens.
- `SPEAKING`: Streaming TTS audio to user's speaker.
- `INTERRUPTED`: Barge-in detected; audio halted, server task cancelled.
- `ERROR`: Graceful failure handled and logged.

## 4. Database Structure
10 core PostgreSQL/SQLite tables:
1. `users` — Authentication & profiles
2. `sessions` — Active auth tokens
3. `conversations` — Conversation threads
4. `messages` — Chat transcript history with display & spoken text
5. `memories` — Extracted user preferences & long-term facts
6. `documents` — Uploaded reference documents
7. `document_chunks` — Split chunks with vector embeddings
8. `tool_calls` — Detailed tool invocation records & latency
9. `agent_tasks` — Multi-step task tracker with confirmation flags
10. `user_preferences` — Voice selection, speed, and privacy flags
