from fastapi import APIRouter
from typing import Dict, Any
import os
from app.core.config import settings
from app.models.response_models import HealthResponse
from app.services.evaluation.metrics import PerformanceMonitor

router = APIRouter()


@router.get("", response_model=Dict[str, Any])
async def get_health():
    """
    Enhanced health check for production readiness.
    Verifies critical dependencies and returns performance summary.
    """
    catalog_exists = os.path.exists("./data/processed/processed_catalog.json")
    vector_index_exists = os.path.exists("./data/vectorstore/faiss.index")
    
    return {
        "status": "ok",
        "version": settings.VERSION,
        "catalog_loaded": catalog_exists,
        "vector_index_loaded": vector_index_exists,
        "performance_metrics": PerformanceMonitor.get_summary()
    }
