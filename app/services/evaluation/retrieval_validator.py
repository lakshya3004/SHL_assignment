from typing import List
from loguru import logger
from app.models.retrieval_models import HybridSearchResult


class RetrievalValidator:
    """
    Ensures that retrieved recommendations are valid, unique, and grounded.
    Prevents duplicates and enforces recommendation count limits.
    """

    MAX_RECOMMENDATIONS = 5
    MIN_DESCRIPTION_LENGTH = 30

    def validate_results(self, results: List[HybridSearchResult]) -> List[HybridSearchResult]:
        """
        Filters and validates the retrieved list of assessments.
        """
        validated = []
        seen_ids = set()

        for res in results:
            # 1. Deduplication
            if res.assessment_id in seen_ids:
                logger.debug(f"Removing duplicate result: {res.assessment_id}")
                continue
            
            # 2. Basic Grounding Check (must have a valid URL and Description)
            if not res.url or "shl.com" not in res.url:
                logger.warning(f"Rejecting result with invalid URL: {res.name}")
                continue
                
            if len(res.description) < self.MIN_DESCRIPTION_LENGTH:
                logger.warning(f"Rejecting result with weak description: {res.name}")
                continue

            validated.append(res)
            seen_ids.add(res.assessment_id)

            # 3. Enforcement of top-k limit
            if len(validated) >= self.MAX_RECOMMENDATIONS:
                break
                
        logger.info(f"Retrieval validation: {len(results)} raw -> {len(validated)} validated.")
        return validated
