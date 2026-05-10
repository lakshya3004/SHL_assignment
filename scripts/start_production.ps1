Write-Host "Starting SHL Recommender in Production Mode..." -ForegroundColor Cyan

# 1. Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found. Create it from .env.example" -ForegroundColor Red
    exit 1
}

# 2. Check for Indices
if (-not (Test-Path "data/vectorstore/faiss.index")) {
    Write-Host "Indices not found. Building indices first..." -ForegroundColor Yellow
    python scripts/build_index.py
}

# 3. Start Uvicorn
Write-Host "Launching FastAPI with 4 workers..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
