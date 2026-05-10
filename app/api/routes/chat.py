from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.services.llm.llm_service import LLMService
from app.services.retrieval.embeddings import EmbeddingService
from app.services.retrieval.vector_store import VectorStore
from app.services.retrieval.keyword_search import KeywordSearchEngine
from app.services.retrieval.hybrid_search import HybridRetriever
from app.services.retrieval.context_builder import RetrievalContextBuilder
from app.services.orchestration.chat_orchestrator import ChatOrchestrator

router = APIRouter()

# Simple dependency injection / singleton setup for Phase 5
# In a full production app, this would be managed by a dependency injection container
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        logger.info("Initializing ChatOrchestrator and sub-services...")
        llm = LLMService()
        embeddings = EmbeddingService()
        v_store = VectorStore()
        v_store.load_index()
        k_engine = KeywordSearchEngine()
        k_engine.load()
        
        retriever = HybridRetriever(v_store, k_engine, embeddings)
        context_builder = RetrievalContextBuilder()
        
        _orchestrator = ChatOrchestrator(llm, retriever, context_builder)
    return _orchestrator


@router.post("", response_model=ChatResponse)
async def chat_with_recommender(
    request: ChatRequest, 
    orchestrator: ChatOrchestrator = Depends(get_orchestrator)
):
    """
    Main entry point for conversational assessment recommendations.
    Uses a multi-stage orchestration pipeline:
    1. Intent Analysis
    2. Grounded Retrieval
    3. Decision Logic (Clarify vs Recommend)
    4. Response Generation
    """
    logger.info(f"Received chat request: {request.message}")
    
    try:
        response = await orchestrator.handle_chat(request)
        return response
        
    except Exception as e:
        logger.error(f"Error in chat orchestration: {str(e)}")
        # Log stack trace if possible in production
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request."
        )
