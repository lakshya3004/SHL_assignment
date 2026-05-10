from typing import List
from loguru import logger
from app.models.orchestration_models import ConversationState, RecommendationDecision
from app.services.retrieval.hybrid_search import HybridRetriever
from app.models.retrieval_models import HybridSearchResult


class RecommendationEngine:
    """
    Decides if we should recommend yet and executes retrieval if so.
    Ensures recommendation quality by enforcing context sufficiency.
    """

    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever

    def evaluate_readiness(self, state: ConversationState) -> RecommendationDecision:
        """
        Determines if there is enough information to make a valid recommendation.
        """
        reqs = state.requirements
        
        # Heuristic: We need a role OR specific skills to match
        if not (reqs.role or reqs.skills):
            return RecommendationDecision(
                should_recommend=False,
                confidence_score=0.2,
                clarification_questions=[
                    "What role or job title are you hiring for?",
                    "What are the most critical skills you need to assess?"
                ],
                reasoning="Missing role and skill context."
            )
            
        return RecommendationDecision(
            should_recommend=True,
            confidence_score=0.8,
            reasoning="Sufficient context provided for a match."
        )

    async def get_candidates(self, state: ConversationState, k: int = 5) -> List[HybridSearchResult]:
        """
        Executes hybrid search based on extracted requirements.
        """
        # Build search query from requirements
        query_parts = []
        if state.requirements.role:
            query_parts.append(state.requirements.role)
        if state.requirements.seniority:
            query_parts.append(state.requirements.seniority)
        
        # Add skill keywords
        query_parts.extend(state.requirements.skills)
        
        # Add preference keywords
        query_parts.extend(state.requirements.test_type_preference)
        
        # Use recent query if it adds value
        if state.intent == "refine":
            query_parts.append(state.recent_query)
            
        search_query = " ".join(query_parts)
        
        logger.info(f"Retrieving candidates for query: {search_query}")
        return self.retriever.search(search_query, k=k)
