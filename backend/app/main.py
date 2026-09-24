import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.database import init_db
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router
from app.api.voice import router as voice_router
from app.api.voice_ws import router as voice_ws_router
from app.api.memory import router as memory_router
from app.api.documents import router as documents_router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("nova.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing NOVA AI Agent backend...")
    await init_db()
    logger.info("NOVA AI Agent backend initialized successfully.")
    yield
    logger.info("NOVA AI Agent backend shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multimodal Real-Time AI Voice Agent - Backend Gateway",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(voice_router, prefix="/api")
app.include_router(voice_ws_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(documents_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "tagline": "A voice-first AI agent that listens, reasons, remembers, and acts.",
        "status": "online",
        "docs_url": "/docs",
        "version": settings.VERSION,
    }
