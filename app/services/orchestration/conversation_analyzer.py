from typing import List, Dict, Any
from loguru import logger
from app.models.orchestration_models import ConversationState, UserRequirements
from app.services.llm.llm_service import LLMService
from app.services.llm import prompts


class ConversationAnalyzer:
    """
    Analyzes conversation history to detect intent and extract requirements.
    Uses LLM-assisted analysis for flexibility with natural language.
    """

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def analyze(self, history: List[Dict[str, str]], latest_message: str) -> ConversationState:
        """
        Runs full analysis on the current conversation turn.
        """
        logger.info("Analyzing conversation turn...")
        
        # Prepare messages for analysis
        analysis_messages = [
            {"role": "system", "content": prompts.ANALYZER_SYSTEM_PROMPT},
            {"role": "user", "content": f"History: {history}\n\nLatest User Message: {latest_message}"}
        ]
        
        analysis_json = await self.llm.generate_json(analysis_messages)
        
        # Extract fields with safe defaults
        intent = analysis_json.get("intent", "clarify")
        req_data = analysis_json.get("requirements", {})
        
        # Determine if requirements are sufficient
        # Logic: Must have at least a role or specific skills/test types
        is_sufficient = bool(req_data.get("role") or req_data.get("skills"))
        
        requirements = UserRequirements(
            role=req_data.get("role"),
            seniority=req_data.get("seniority"),
            skills=req_data.get("skills", []),
            hiring_goals=req_data.get("hiring_goals", []),
            test_type_preference=req_data.get("test_type_preference", []),
            is_sufficient=is_sufficient
        )
        
        # Heuristic override: if intent is 'recommend' but requirements are empty, force 'clarify'
        if intent == "recommend" and not is_sufficient:
            intent = "clarify"

        # Check for off-topic via keyword + LLM
        if self._is_off_topic_heuristic(latest_message) or intent == "refuse":
            intent = "refuse"

        return ConversationState(
            intent=intent,
            requirements=requirements,
            recent_query=latest_message,
            turn_count=len(history) // 2 + 1
        )

    def _is_off_topic_heuristic(self, message: str) -> bool:
        """Simple fast check for obvious off-topic or injection attempts."""
        off_topic_keywords = ["weather", "pizza", "joke", "poem", "ignore previous instructions"]
        msg_lower = message.lower()
        return any(kw in msg_lower for kw in off_topic_keywords)
