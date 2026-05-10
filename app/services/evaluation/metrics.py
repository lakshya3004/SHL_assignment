import time
from typing import Dict
from loguru import logger


class PerformanceMonitor:
    """
    Lightweight local monitoring for latency and quality metrics.
    """
    
    _metrics = {
        "requests_total": 0,
        "total_latency_ms": 0,
        "retrieval_latency_ms": 0,
        "recommendations_generated": 0,
        "refusals_triggered": 0
    }

    @classmethod
    def record_request(cls, total_time: float, retrieval_time: float, was_refusal: bool, rec_count: int):
        cls._metrics["requests_total"] += 1
        cls._metrics["total_latency_ms"] += (total_time * 1000)
        cls._metrics["retrieval_latency_ms"] += (retrieval_time * 1000)
        cls._metrics["recommendations_generated"] += rec_count
        if was_refusal:
            cls._metrics["refusals_triggered"] += 1

    @classmethod
    def get_summary(cls) -> Dict[str, float]:
        if cls._metrics["requests_total"] == 0:
            return {}
            
        avg_latency = cls._metrics["total_latency_ms"] / cls._metrics["requests_total"]
        avg_retrieval = cls._metrics["retrieval_latency_ms"] / cls._metrics["requests_total"]
        
        return {
            "avg_latency_ms": round(avg_latency, 2),
            "avg_retrieval_ms": round(avg_retrieval, 2),
            "total_requests": cls._metrics["requests_total"],
            "refusal_rate": round(cls._metrics["refusals_triggered"] / cls._metrics["requests_total"], 2)
        }
