from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """
    Represents a single message in the conversation.
    """
    role: str = Field(..., description="The role of the message sender (user or assistant)")
    content: str = Field(..., description="The text content of the message")


class ChatRequest(BaseModel):
    """
    Request schema for the chat endpoint.
    Stateless, so it should ideally receive the conversation history or relevant context.
    """
    message: str = Field(..., description="The latest user message")
    history: List[ChatMessage] = Field(default_factory=list, description="Previous messages in the conversation")
    
    # Optional fields for future use cases
    session_id: Optional[str] = Field(None, description="Unique identifier for the session")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional context or metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "I need a test for logical reasoning in a corporate setting.",
                "history": [],
                "session_id": "sess_12345"
            }
        }
    }
