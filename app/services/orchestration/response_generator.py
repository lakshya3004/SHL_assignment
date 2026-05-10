from typing import List, Dict
from loguru import logger
from app.services.llm.llm_service import LLMService
from app.services.llm import prompts
from app.models.retrieval_models import RetrievalContext


class ResponseGenerator:
    """
    Generates the final conversational response.
    Ensures tone is professional, concise, and grounded.
    """

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def generate_response(
        self, 
        query: str, 
        context: RetrievalContext, 
        intent: str,
        history: List[Dict[str, str]]
    ) -> str:
        """
        Main response generation entry point.
        """
        logger.info(f"Generating grounded response for intent: {intent}")
        
        # Tailor the prompt slightly based on intent if needed
        system_prompt = prompts.RESPONSE_SYSTEM_PROMPT
        
        if intent == "clarify":
            system_prompt += "\nSpecific Goal: Ask clarifying questions to narrow down the assessment choice."
        elif intent == "refine":
            system_prompt += "\nSpecific Goal: Acknowledge the refinement and update recommendations accordingly."

        messages = [
            {"role": "system", "content": system_prompt},
            # Add context documents as separate system/user context
            {"role": "user", "content": f"### AVAILABLE SHL ASSESSMENTS:\n{context.context_text}"}
        ]
        
        # Add conversation history
        for turn in history[-4:]: # Only last 2 turns for conciseness
            messages.append(turn)
            
        # Add latest query
        messages.append({"role": "user", "content": query})
        
        return await self.llm.generate_completion(messages, temperature=0.4)
