from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class RawAssessment(BaseModel):
    """
    Represents the raw, uncleaned data scraped from the SHL catalog.
    Used for initial persistence to avoid re-scraping during development.
    """
    name: str
    url: str
    raw_html: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProcessedAssessment(BaseModel):
    """
    Cleaned and normalized assessment data ready for ranking and orchestration.
    """
    id: str = Field(..., description="Unique slug or ID derived from the name/URL")
    name: str = Field(..., description="Cleaned assessment name")
    url: str = Field(..., description="Full verified URL to the assessment page")
    description: str = Field(..., description="Sanitized and normalized description text")
    test_type: str = Field(..., description="Standardized category (e.g., Cognitive, Behavioral)")
    duration: Optional[str] = Field(None, description="Test duration if available")
    remote_support: bool = Field(default=False, description="Whether remote testing is supported")
    adaptive: bool = Field(default=False, description="Whether the test is adaptive/IRT based")
    keywords: List[str] = Field(default_factory=list, description="Extracted searchable keywords")
    source: str = "shl_catalog"
    ingestion_timestamp: datetime = Field(default_factory=datetime.now)
    processed_at: datetime = Field(default_factory=datetime.now)
    validation_status: str = Field(default="pending", description="Status of quality validation")
    quality_score: float = Field(default=0.0, description="Calculated quality score from 0.0 to 1.0")


class RetrievalDocument(BaseModel):
    """
    Optimized format for vector database ingestion.
    """
    assessment_id: str
    text: str = Field(..., description="Concatenated text optimized for semantic search")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for filtering (type, remote, etc.)")
