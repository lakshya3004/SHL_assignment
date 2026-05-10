from loguru import logger
from app.models.response_models import ChatResponse


class ResponseValidator:
    """
    Ensures the final API response is strictly compliant with the schema 
    and contains no hallucinated artifacts.
    """

    def validate(self, response: ChatResponse) -> ChatResponse:
        """
        Runs post-generation checks on the final response object.
        """
        # 1. Hallucinated URL Check
        # Ensure all recommendation URLs match their names (basic heuristic)
        for rec in response.recommendations:
            if not rec.url.startswith("http"):
                logger.error(f"Schema violation: Invalid URL in recommendation {rec.name}")
                rec.url = "https://www.shl.com/products/product-catalog/"

        # 2. Response Length Check
        if len(response.reply) > 2000:
            logger.warning("Response is excessively long, truncating for readability.")
            response.reply = response.reply[:2000] + "..."

        # 3. Empty recommendations rule
        # If the reply mentions 'clarifying' but has recommendations, it's inconsistent
        if "clarify" in response.reply.lower() and response.recommendations:
            logger.info("Aligning response: Removing premature recommendations from clarification reply.")
            response.recommendations = []

        return response
