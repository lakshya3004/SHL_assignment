# SHL Assessment Recommender System

A production-quality AI-powered conversational recommender for SHL assessments.

## Features
- **Stateless Conversations**: Efficient chat management.
- **RAG Pipeline**: Grounded responses using SHL assessment catalog.
- **Robust Refusal**: Prompt injection resistance and hallucination prevention.
- **Clean Architecture**: Modular and scalable design.

## Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **LLM**: OpenAI-compatible wrappers
- **Embeddings**: SentenceTransformers
- **Vector Store**: FAISS
- **Testing**: Pytest

## Project Structure
```text
project-root/
├── app/                  # Main application code
│   ├── api/              # API routes and router logic
│   ├── core/             # Config, logging, security
│   ├── models/           # Pydantic schemas (request/response)
│   ├── services/         # Business logic (RAG, Ingestion, etc.)
│   └── utils/            # Shared utilities
├── data/                 # Raw and processed assessment data
├── scripts/              # Helper scripts for ingestion
└── tests/                # Unit and integration tests
```

## Getting Started

### Prerequisites
- Python 3.11 or higher
- pip or poetry

### Setup
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd project-root
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in your details.
   ```bash
   cp .env.example .env
   ```

## 🚀 Production Deployment

### Option 1: Docker (Recommended)
```bash
docker-compose up --build
```
The API will be available at `http://localhost:8000`.

### Option 2: Local Production (Windows)
```powershell
.\scripts\start_production.ps1
```

## 🧪 Evaluation & Testing

### 1. Stress Testing (Guardrails)
Validate the system's resistance to prompt injection, jailbreaks, and off-topic queries.
```bash
python scripts/evaluator_tests.py
```

### 2. Performance Benchmarking
Measure end-to-end latency and retrieval efficiency.
```bash
python scripts/benchmark.py
```

### 3. API Examples

**Post-Request (Chat):**
```json
POST /api/v1/chat
{
  "message": "I'm hiring a Java Developer",
  "history": []
}
```

**Health Check:**
```json
GET /api/v1/health
```

## 🏗️ Architecture
For a detailed breakdown of our RAG strategy, orchestration logic, and hallucination prevention, please see [APPROACH.md](./APPROACH.md).

## 🛠️ Troubleshooting
- **Missing Indices**: If retrieval fails, run `python scripts/build_index.py`.
- **LLM Timeouts**: Check your `OPENAI_API_KEY` and ensure the `LLM_BASE_URL` is accessible.
- **Port Conflicts**: Uvicorn defaults to `8000`. Change this in `docker-compose.yml` if needed.
