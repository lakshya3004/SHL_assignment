from typing import List
from datetime import datetime
from app.models.retrieval_models import HybridSearchResult, RetrievalContext


class RetrievalContextBuilder:
    """
    Formats retrieved assessments into a grounded context string for the LLM.
    Ensures that descriptions, URLs, and categories are preserved.
    """

    @staticmethod
    def build_context(query: str, results: List[HybridSearchResult]) -> RetrievalContext:
        """
        Constructs the markdown-formatted context block.
        """
        if not results:
            return RetrievalContext(
                context_text="No relevant assessments found in the SHL catalog for this query.",
                results=[],
                query=query,
                retrieved_at=str(datetime.now())
            )

        context_parts = []
        context_parts.append("Below are the relevant SHL assessments retrieved from the catalog based on the user's request. You MUST use these to provide recommendations.\n")
        
        for res in results:
            item_text = (
                f"ASSESSMENT:\n"
                f"Name: {res.name}\n"
                f"Category: {res.test_type}\n"
                f"Description: {res.description}\n"
                f"URL: {res.url}\n"
            )
            context_parts.append(item_text)

        final_text = "\n".join(context_parts)
        
        return RetrievalContext(
            context_text=final_text,
            results=results,
            query=query,
            retrieved_at=str(datetime.now())
        )

    # TODO: Add logic to filter out low-score results if they fall below a dynamic threshold
    # TODO: Implement 'refinement' context which combines current results with previous session context
