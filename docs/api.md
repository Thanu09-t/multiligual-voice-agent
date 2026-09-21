# NOVA API Documentation

## REST Endpoints

### Health
- `GET /api/health`: System health, DB connection, uptime, active providers.

### Authentication
- `POST /api/auth/register`: Register new user (`email`, `password`, `full_name`).
- `POST /api/auth/login`: Authenticate and receive JWT access token.
- `GET /api/auth/me`: Current user profile.

### Conversations
- `GET /api/conversations`: List user conversations.
- `POST /api/conversations`: Create new conversation.
- `GET /api/conversations/{id}`: Fetch conversation messages and history.
- `DELETE /api/conversations/{id}`: Delete conversation.

### Chat
- `POST /api/chat`: Send text message, run agent loop, return response and tool actions.

### Voice & Audio
- `POST /api/voice/transcribe`: Transcribe uploaded audio file to text.
- `POST /api/voice/synthesize`: Synthesize text to spoken audio bytes.
- `WS /api/voice`: Real-time bi-directional streaming WebSocket for voice, VAD, STT, and TTS.

### Documents & RAG
- `POST /api/documents/upload`: Upload PDF/TXT/DOCX for text extraction and vector indexing.
- `GET /api/documents`: List user uploaded documents and chunk statistics.
- `DELETE /api/documents/{id}`: Remove document and its vector chunks.
- `POST /api/documents/search`: Semantic vector search query over indexed chunks.

### Memory
- `GET /api/memory`: List user long-term memories.
- `DELETE /api/memory`: Clear user memories (supports category filter).
- `DELETE /api/memory/{id}`: Delete single memory item.

## WebSocket Voice Protocol
Connect to `ws://localhost:8000/api/voice?token=<jwt_token>`.

### Client Event Types
- `audio_chunk`: Base64 encoded audio fragment from mic.
- `speech_started`: User began speaking.
- `speech_stopped`: User stopped speaking (silence detected).
- `text_input`: Direct text message.
- `interrupt`: Immediate barge-in trigger.
- `tool_confirmation`: User confirmed or rejected a tool execution.

### Server Event Types
- `transcript_partial`: Streaming partial transcription.
- `transcript_final`: Completed transcription.
- `agent_status`: Current agent state (`IDLE`, `LISTENING`, `THINKING`, `USING_TOOL`, `GENERATING`, `SPEAKING`, `INTERRUPTED`, `ERROR`).
- `tool_status`: Tool execution progress indicator.
- `response_chunk`: Streaming LLM response token.
- `response_text`: Completed response (includes `display_text` and `spoken_text`).
- `tts_audio_chunk`: Base64 streaming audio chunk for playback.
- `awaiting_confirmation`: Tool confirmation prompt.
- `interrupted`: Confirmed barge-in cancellation.
- `error`: Error details and user-safe message.
