# NOVA Setup & Installation Guide

## Prerequisites
- **Python 3.10+** (Tested on Python 3.14)
- **Node.js 18+** (Tested on Node 22)
- **npm** or **pnpm**
- (Optional) **Docker** & **PostgreSQL**

## 1. Backend Setup

```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
# On Windows: venv\Scripts\activate
# On Unix: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your provider keys if desired

# Run Backend
uvicorn app.main:app --reload --port 8000
```

Verify backend health at: `http://localhost:8000/api/health`

## 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run Frontend Dev Server
npm run dev
```

Open `http://localhost:3000` in your browser.

## 3. Docker Setup (Alternative)

```bash
docker-compose up --build
```
