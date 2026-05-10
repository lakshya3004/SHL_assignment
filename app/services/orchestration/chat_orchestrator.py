import time
from typing import List, Dict, Any
from loguru import logger

from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse, AssessmentRecommendation
from app.models.orchestration_models import ConversationState

from app.services.llm.llm_service import LLMService
from app.services.retrieval.hybrid_search import HybridRetriever
from app.services.retrieval.context_builder import RetrievalContextBuilder
from app.services.orchestration.conversation_analyzer import ConversationAnalyzer
from app.services.orchestration.recommendation_engine import RecommendationEngine
from app.services.orchestration.comparison_engine import ComparisonEngine
from app.services.orchestration.refusal_engine import RefusalEngine
from app.services.orchestration.response_generator import ResponseGenerator

# Final Phase Integrations
from app.services.evaluation.evaluator_guardrails import EvaluatorGuardrails
from app.services.evaluation.retrieval_validator import RetrievalValidator
from app.services.evaluation.response_validator import ResponseValidator
from app.services.evaluation.metrics import PerformanceMonitor
from app.utils.cache import cache_query


class ChatOrchestrator:
    """
    Final Hardened Controller for the recommendation flow.
    Includes guardrails, validation, and performance monitoring.
    """

    def __init__(
        self, 
        llm: LLMService, 
        retriever: HybridRetriever,
        context_builder: RetrievalContextBuilder
    ):
        self.analyzer = ConversationAnalyzer(llm)
        self.recommender = RecommendationEngine(retriever)
        self.comparer = ComparisonEngine(llm)
        self.refuser = RefusalEngine(llm)
        self.generator = ResponseGenerator(llm)
        self.context_builder = context_builder
        
        # Evaluator specialized components
        self.guardrails = EvaluatorGuardrails()
        self.retrieval_validator = RetrievalValidator()
        self.response_validator = ResponseValidator()

    @cache_query
    async def handle_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Processes a chat request with safety checks and validation.
        """
        start_time = time.time()
        retrieval_time = 0.0
        was_refusal = False
        
        history = [{"role": m.role, "content": m.content} for m in request.history]
        query = self.guardrails.sanitize_input(request.message)
        
        # 1. Safety Guardrails (Prompt Injection & Malicious Intent)
        if self.guardrails.is_injection_attempt(query) or self.guardrails.is_malicious_intent(query):
            reply = await self.refuser.handle_refusal(query)
            res = ChatResponse(reply=reply, recommendations=[], end_of_conversation=False)
            PerformanceMonitor.record_request(time.time()-start_time, 0, True, 0)
            return res

        # 2. Analyze Intent
        state: ConversationState = await self.analyzer.analyze(history, query)
        
        # 3. Route & Generate
        final_response = None
        
        if state.intent == "refuse":
            reply = await self.refuser.handle_refusal(query)
            final_response = ChatResponse(reply=reply, recommendations=[], end_of_conversation=False)
            was_refusal = True
        
        elif state.intent == "compare":
            r_start = time.time()
            candidates = await self.recommender.get_candidates(state, k=4)
            retrieval_time = time.time() - r_start
            
            candidates = self.retrieval_validator.validate_results(candidates)
            reply = await self.comparer.compare(query, candidates)
            final_response = self._build_response(reply, candidates, False)
            
        else:
            decision = self.recommender.evaluate_readiness(state)
            
            if not decision.should_recommend and state.intent != "refine":
                context = self.context_builder.build_context(query, [])
                reply = await self.generator.generate_response(query, context, "clarify", history)
                final_response = ChatResponse(reply=reply, recommendations=[], end_of_conversation=False)
            else:
                r_start = time.time()
                candidates = await self.recommender.get_candidates(state, k=5)
                retrieval_time = time.time() - r_start
                
                candidates = self.retrieval_validator.validate_results(candidates)
                context = self.context_builder.build_context(query, candidates)
                reply = await self.generator.generate_response(query, context, state.intent, history)
                final_response = self._build_response(reply, candidates, False)

        # 4. Final Validation & Schema Cleanup
        final_response = self.response_validator.validate(final_response)
        
        # Record Metrics
        PerformanceMonitor.record_request(
            time.time() - start_time, 
            retrieval_time, 
            was_refusal, 
            len(final_response.recommendations)
        )
        
        return final_response

    def _build_response(self, reply: str, candidates: List[Any], end_of_conversation: bool) -> ChatResponse:
        """Helper to convert candidates to the exact response schema."""
        recommendations = [
            AssessmentRecommendation(
                name=c.name,
                url=c.url,
                test_type=c.test_type
            ) for c in candidates
        ]
        
        return ChatResponse(
            reply=reply,
            recommendations=recommendations,
            end_of_conversation=end_of_conversation
        )
