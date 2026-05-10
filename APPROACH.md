# SHL Assessment Recommender: Technical Approach

Approach Document
System Design

The system is designed as a production-oriented conversational recommender for SHL assessments using a Retrieval-Augmented Generation (RAG) architecture. The backend is implemented using FastAPI with a modular structure separating ingestion, retrieval, orchestration, evaluation, and API layers.

The workflow consists of:

Catalog Ingestion
SHL assessment catalog pages are scraped and normalized into structured documents.
Only Individual Test Solutions are retained. Bundled or unrelated offerings are filtered during ingestion.
Metadata such as assessment category, description, keywords, duration, and URLs are preserved for retrieval and grounding.
Retrieval Layer
Dense semantic retrieval using SentenceTransformers (all-MiniLM-L6-v2) with FAISS.
Sparse keyword retrieval using TF-IDF.
Reciprocal Rank Fusion (RRF) combines both retrieval methods to improve Recall@10 and exact-skill matching.
Conversational Orchestration
A deterministic orchestration layer analyzes intent, determines whether clarification is needed, performs retrieval, and generates grounded responses.
The system avoids autonomous agent loops to reduce hallucination risk and improve evaluation consistency.
Validation & Guardrails
Prompt injection detection, schema validation, retrieval validation, and refusal handling are applied before responses are returned.
Retrieval Setup

A hybrid retrieval setup was chosen because semantic-only retrieval struggled with recruiter-style keyword queries such as:

“Java backend developer”
“numerical reasoning”
“leadership hiring”

Dense embeddings handled semantic intent well but occasionally missed exact assessment names or technical skill matches. Sparse TF-IDF retrieval improved precision for exact terminology and recruiter-specific keywords.

Final retrieval flow:

Query embedding generation
FAISS semantic search
TF-IDF keyword search
Reciprocal Rank Fusion (RRF)
Deduplication and reranking

Retrieval chunks were optimized to include:

assessment name
category
measurable skills
cleaned descriptions
source URLs

This improved both retrieval relevance and grounding quality.

Prompt & Conversation Design

The orchestration layer follows a clarification-first strategy.

The assistant avoids immediate recommendations for vague prompts. For example:

“I need an assessment” triggers clarification questions about role, seniority, and hiring goals before retrieval is executed.

Conversation analysis supports:

vague query detection
refinement handling
comparison requests
off-topic refusal
prompt injection detection

The LLM is instructed to:

only use retrieved SHL context
never invent assessments or URLs
refuse unsupported comparisons
avoid non-SHL recommendations

Comparison responses are grounded entirely in retrieved catalog metadata and processed descriptions.

The system is fully stateless. Each request contains the complete conversation history, and no session state is stored server-side.

Evaluation Approach

Testing focused on:

Recall@10 quality
conversational robustness
schema compliance
latency
hallucination resistance

Manual evaluation scenarios included:

vague recruiter prompts
refinement conversations
comparison requests
prompt injection attempts
malformed payloads
off-topic questions

Benchmark scripts were used to measure:

retrieval latency
orchestration latency
end-to-end API response time

The target response latency was under 5 seconds locally.

What Did Not Work
Pure semantic retrieval
Produced weaker exact-skill matching and inconsistent recruiter query performance.
Agentic orchestration
Autonomous multi-step agents increased unpredictability and hallucination risk.
Deterministic orchestration was more stable for evaluator-focused testing.
Unfiltered catalog ingestion
Including bundled SHL solutions reduced retrieval quality and occasionally surfaced out-of-scope recommendations.
Large retrieval contexts
Passing excessive context to the LLM increased latency and reduced response consistency.
AI Tooling Disclosure

AI-assisted coding tools were used for:

project scaffolding
boilerplate generation
iterative implementation
documentation drafting
test scenario generation

All retrieval logic, orchestration behavior, filtering rules, validation flows, and evaluation strategies were manually reviewed, modified, and tested during development.
