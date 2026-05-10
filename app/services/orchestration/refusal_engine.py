from loguru import logger
from app.services.llm.llm_service import LLMService
from app.services.llm import prompts


class RefusalEngine:
    """
    Handles off-topic, unsafe, or out-of-scope queries.
    Politely redirects the user back to the SHL assessment domain.
    """

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def handle_refusal(self, query: str) -> str:
        """
        Generates a polite refusal message.
        """
        logger.info(f"Handling refusal for query: {query[:50]}...")
        
        messages = [
            {"role": "system", "content": prompts.REFUSAL_SYSTEM_PROMPT},
            {"role": "user", "content": f"User asked: {query}"}
        ]
        
        response = await self.llm.generate_completion(messages, temperature=0.5)
        return response
