from typing import List, Optional
from pydantic import BaseModel, Field


class AssessmentRecommendation(BaseModel):
    """
    Schema for a single SHL assessment recommendation.
    """
    name: str = Field(..., description="The name of the assessment")
    url: str = Field(..., description="Official URL or link to the assessment details")
    test_type: str = Field(..., description="The category or type of test (e.g., Cognitive, Behavioral)")


class ChatResponse(BaseModel):
    """
    Strict response schema for the AI recommender chat endpoint.
    This matches the requirements specified for evaluation.
    """
    reply: str = Field(..., description="The conversational response from the AI assistant")
    recommendations: List[AssessmentRecommendation] = Field(
        default_factory=list, 
        description="List of recommended assessments from the SHL catalog"
    )
    end_of_conversation: bool = Field(
        default=False, 
        description="Flag indicating if the conversation has reached a natural conclusion"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "reply": "Based on your requirements, I recommend the SHL Deductive Reasoning test.",
                "recommendations": [
                    {
                        "name": "Deductive Reasoning",
                        "url": "https://www.shl.com/deductive-reasoning",
                        "test_type": "Cognitive"
                    }
                ],
                "end_of_conversation": False
            }
        }
    }


class HealthResponse(BaseModel):
    """
    Schema for the health check endpoint response.
    """
    status: str = "ok"
    version: str
    debug_mode: bool
