# NOVA — Multimodal Real-Time AI Voice Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> *"A voice-first AI agent that listens, reasons, remembers, and acts."*

---

## 🌟 Highlights

- 🎙️ **Real-Time Voice Conversation**: Low-latency bi-directional voice streaming over WebSocket.
- ⚡ **Zero-Latency Barge-In (Interruption)**: Client-side Voice Activity Detection (VAD) instantly halts speech and cancels server tasks when the user begins speaking.
- 🧠 **Multi-Step Agent Reasoning**: Intent parsing, task planning, and tool orchestration.
- 🛠️ **Extensible Tool Registry**: Built-in Calculator, Weather, Web Search, and File Search with safety confirmation for consequential actions.
- 📚 **Document RAG Intelligence**: PDF, DOCX, and TXT parsing, semantic chunking, and vector retrieval.
- 💾 **Dual-Layer Memory**: Short-term sliding conversation context + persistent long-term user facts and preferences.
- 🔮 **Futuristic AI OS Interface**: Interactive dynamic AI Voice Orb reacting to state and audio energy, live Web Audio API waveform visualizer, and dark glassmorphic styling.
- 🧩 **Modular AI Providers**: Easily swap LLM (OpenAI, Groq, Gemini), STT (Whisper, Groq), and TTS (Edge-TTS, OpenAI) engines without altering core agent logic.

---

## 🏛️ Architecture

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

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to interact with NOVA.

---

## ⚙️ Environment Configuration

Refer to [`backend/.env.example`](backend/.env.example) for the full list of configuration options including API keys, database connection strings, and provider selectors.

---

## 📖 Documentation

- [System Architecture](docs/architecture.md)
- [Setup & Installation](docs/setup.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)
