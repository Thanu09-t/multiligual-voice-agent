# NOVA Deployment Guide

## 1. Environments

### Development
- Local SQLite database or local Docker PostgreSQL.
- Frontend on `http://localhost:3000`, Backend on `http://localhost:8000`.
- Mock providers enabled for offline zero-cost testing.

### Staging
- Managed PostgreSQL (AWS RDS / Supabase / Neon).
- Backend deployed on container platform (Render / Fly.io / AWS ECS) with WebSocket support.
- Frontend deployed on Vercel with environment variable pointing to backend WebSocket/REST URL.

### Production
- Production PostgreSQL with connection pooling (e.g. pgBouncer).
- SSL/TLS terminated at ingress (WSS for WebSockets, HTTPS for REST).
- Set `ENVIRONMENT=production`, secure `JWT_SECRET`, strict `CORS_ORIGINS`.
- API keys set in secret manager (AWS Secrets Manager, GCP Secret Manager, or platform env).

## 2. Docker Deployment
```bash
docker-compose -f docker-compose.yml up -d --build
```
