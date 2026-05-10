from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class UserRequirements(BaseModel):
    """
    Extracted hiring requirements from the conversation history.
    """
    role: Optional[str] = None
    seniority: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    hiring_goals: List[str] = Field(default_factory=list)
    test_type_preference: List[str] = Field(default_factory=list)
    is_sufficient: bool = Field(default=False, description="Whether we have enough info to recommend")


class ConversationState(BaseModel):
    """
    Maintains the state of the current conversation for orchestration decisions.
    """
    intent: str = Field(..., description="Detected intent: recommend, clarify, compare, refuse, refine")
    requirements: UserRequirements
    recent_query: str
    history_summary: Optional[str] = None
    turn_count: int = 0


class ComparisonRequest(BaseModel):
    """
    Structured data for a comparison request between assessments.
    """
    assessment_names: List[str]
    specific_aspects: List[str] = Field(default_factory=list)


class RecommendationDecision(BaseModel):
    """
    Decision output from the recommendation engine.
    """
    should_recommend: bool
    confidence_score: float
    clarification_questions: List[str] = Field(default_factory=list)
    reasoning: str
