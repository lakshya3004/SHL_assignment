# SHL Assessment Recommender: Technical Approach

## 1. System Architecture
The system is built with a **modular, deterministic orchestration** architecture using FastAPI. It avoids complex autonomous agents in favor of a predictable pipeline:
- **API Layer**: FastAPI with strict Pydantic validation.
- **Orchestration**: A centralized controller that manages intent detection, retrieval gating, and grounded response generation.
- **Storage**: JSON-based catalog with FAISS vector indices and TF-IDF sparse matrices.

## 2. Retrieval Strategy
To achieve high **Recall@10**, we use a **Hybrid Retrieval** system:
- **Dense Retrieval**: `sentence-transformers/all-MiniLM-L6-v2` for semantic intent matching.
- **Sparse Retrieval**: `TF-IDF` for exact matches on product names (e.g., "OPQ32") and specific skill keywords.
- **Rank Fusion**: Reciprocal Rank Fusion (RRF) merges results to surface the best candidates from both worlds.

## 3. Conversation Orchestration
The orchestrator follows a **"Clarify Before Recommend"** strategy:
- **Analyzer**: Extracts hiring signals (role, seniority, skills) using LLM-assisted JSON parsing.
- **Decision Engine**: Blocks recommendations if requirements are insufficient, triggering targeted clarifying questions.
- **Refinement**: Preserves state by augmenting retrieval queries with historical context.

## 4. Hallucination Prevention
Grounding is enforced at multiple layers:
- **Ingestion**: Strict filtering of non-assessment products.
- **Retrieval**: Only verified catalog entries enter the context window.
- **Validation**: Post-generation schema validation ensures URLs and counts are accurate.
- **Negative Constraint**: System prompts strictly prohibit inventing assessments or URLs.

## 5. Evaluation & Hardening
- **Heuristic Guardrails**: Detects prompt injection and jailbreak patterns without expensive moderation APIs.
- **Caching**: In-memory query caching reduces latency for repeated refinements.
- **Resilience**: 15s LLM timeouts and graceful fallbacks prevent cascading failures during evaluation.

## 6. Tradeoffs
- **LLM vs Rules**: We used LLM for intent/extraction but rules for routing and filtering to ensure explainability and speed.
- **Lightweight Embeddings**: Chose `all-MiniLM-L6-v2` over larger models to keep local inference under 1 second.

## 7. AI Tooling Disclosure
Developed using **Antigravity** (Google Deepmind AI assistant) for scaffolding and implementation support. All business logic and orchestration patterns were engineered for production-grade robustness.
