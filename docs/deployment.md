# NOVA Deployment Guide

This guide outlines how to deploy NOVA to production, specifically deploying the **Frontend to Vercel** and the **FastAPI Backend to Render / Railway / Fly.io** (which supports persistent WebSockets required for real-time voice).

---

## 🏛️ Deployment Architecture

```
┌──────────────────────────────────────────────┐
│  Vercel (Frontend - Next.js 14)             │
│  - Hosted on: https://your-nova.vercel.app   │
│  - Client-side VAD, Audio Orb & UI           │
└──────────────────────┬───────────────────────┘
                       │ HTTPS & WSS (WebSockets)
                       ▼
┌──────────────────────────────────────────────┐
│  Render / Railway / Fly.io (Backend FastAPI) │
│  - Hosted on: https://your-backend.onrender.com
│  - WebSocket: wss://your-backend.onrender.com │
│  - STT, LLM, TTS, Tools, & RAG Engine        │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Managed PostgreSQL (Neon / Supabase / Render)
└──────────────────────────────────────────────┘
```

---

## 🚀 Step 1: Push Your Repository to GitHub

Ensure your code is pushed to your GitHub repository:

```bash
git branch -M main
git push -u origin main
```

---

## 🖥️ Step 2: Deploy the Backend (FastAPI with WebSockets)

Because real-time voice requires persistent, bidirectional WebSockets, deploy the backend to a platform like **Render**, **Railway**, or **Fly.io**.

### Deploying on Render (Recommended Free/Simple):
1. Sign up/Log in at [render.com](https://render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository: `chatbot_chitra`.
4. Configure the service settings:
   - **Name**: `nova-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `ENVIRONMENT`: `production`
   - `CORS_ORIGINS`: `https://your-nova.vercel.app,http://localhost:3000` *(update once you have your Vercel URL)*
   - `JWT_SECRET`: *(generate a random 32-character secret string)*
   - `GROQ_API_KEY`: *(your Groq API key)*
   - `GEMINI_API_KEY`: *(your Gemini API key)*
   - `DATABASE_URL`: `sqlite+aiosqlite:///./nova.db` *(or PostgreSQL URL from Neon/Supabase)*
   - `LLM_PROVIDER`: `groq`
   - `LLM_MODEL`: `openai/gpt-oss-20b`
   - `STT_PROVIDER`: `groq`
   - `TTS_PROVIDER`: `mock` *(or `openai` if you have TTS key)*
6. Click **Create Web Service**.
7. Copy your assigned backend URL: e.g., `https://nova-backend.onrender.com`.

---

## ⚡ Step 3: Deploy the Frontend to Vercel

1. Log in to [vercel.com](https://vercel.com) using your GitHub account.
2. On your Vercel Dashboard, click **Add New...** -> **Project**.
3. Import your GitHub repository: `chatbot_chitra`.
4. Configure the project:
   - **Framework Preset**: `Next.js` (automatically detected).
   - **Root Directory**: Click **Edit** and choose `frontend`.
   - **Build Command**: `npm run build` (default).
   - **Output Directory**: `.next` (default).
5. Expand **Environment Variables** and add the following two variables:
   - `NEXT_PUBLIC_API_URL`: `https://nova-backend.onrender.com` *(your backend HTTPS URL from Step 2)*
   - `NEXT_PUBLIC_WS_URL`: `wss://nova-backend.onrender.com` *(your backend WSS URL from Step 2)*
6. Click **Deploy**.
7. Vercel will build and assign your live domain (e.g., `https://nova-voice-agent.vercel.app`).

---

## 🔄 Step 4: Final Link & CORS Update

1. Go back to your backend deployment settings (e.g. on Render/Railway).
2. Update the `CORS_ORIGINS` environment variable to include your actual Vercel production URL:
   ```
   CORS_ORIGINS=https://your-project.vercel.app,http://localhost:3000
   ```
3. Restart or redeploy the backend service.
4. Visit your Vercel URL (`https://your-project.vercel.app`), click the microphone icon, and start speaking with NOVA!

---

## 🧪 Verification Checklist

- [ ] Vercel frontend builds without errors.
- [ ] Visiting `/api/health` on your backend returns `{"status": "healthy"}`.
- [ ] Frontend WebSocket establishes connection (`wss://.../api/voice`).
- [ ] Speech input & visualizer waveform react to microphone input.
