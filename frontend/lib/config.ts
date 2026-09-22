/**
 * Centralized API & WebSocket configuration for NOVA.
 * Supports custom production domains via NEXT_PUBLIC_API_URL and NEXT_PUBLIC_WS_URL.
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") || "http://127.0.0.1:8000";

export const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL?.replace(/\/+$/, "") || "ws://127.0.0.1:8000";

export const APP_CONFIG = {
  name: "NOVA",
  tagline: "Multimodal AI Voice Agent",
  repoUrl: "https://github.com/Thanu09-t/multiligual-voice-agent",
  version: "1.0.0",
};
