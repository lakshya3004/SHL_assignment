from typing import List, Dict
from loguru import logger
from app.services.llm.llm_service import LLMService
from app.services.llm import prompts
from app.models.retrieval_models import HybridSearchResult


class ComparisonEngine:
    """
    Handles comparison requests between SHL assessments.
    Strictly grounds comparisons in retrieved catalog data.
    """

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def compare(self, query: str, context_docs: List[HybridSearchResult]) -> str:
        """
        Generates a grounded comparison between assessments in the context.
        """
        logger.info(f"Generating comparison for: {query}")
        
        # Format the context for the comparison prompt
        context_str = "\n".join([
            f"ASSESSMENT: {res.name}\nType: {res.test_type}\nDescription: {res.description}" 
            for res in context_docs
        ])
        
        messages = [
            {"role": "system", "content": prompts.COMPARISON_SYSTEM_PROMPT},
            {"role": "user", "content": f"Context Assessments:\n{context_str}\n\nComparison Query: {query}"}
        ]
        
        return await self.llm.generate_completion(messages, temperature=0.3)
