from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """
    Represents a single result from an individual search engine (Vector or Keyword).
    """
    assessment_id: str
    name: str
    score: float = Field(..., description="The relevance score from the specific engine")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HybridSearchResult(BaseModel):
    """
    Represents a result after hybrid rank fusion.
    """
    assessment_id: str
    name: str
    url: str
    test_type: str
    description: str
    combined_score: float = Field(..., description="The fused rank score (e.g., RRF score)")
    rank: int = Field(..., description="The final rank position in the combined results")


class RetrievalContext(BaseModel):
    """
    The final context payload ready to be injected into an LLM prompt.
    """
    context_text: str = Field(..., description="Grounded markdown-formatted assessment list")
    results: List[HybridSearchResult] = Field(default_factory=list)
    query: str
    retrieved_at: str
