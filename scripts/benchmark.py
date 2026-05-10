import asyncio
import time
import sys
import os
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.request_models import ChatRequest
from app.api.routes.chat import get_orchestrator
from app.services.evaluation.metrics import PerformanceMonitor

async def run_benchmark():
    orchestrator = get_orchestrator()
    
    benchmark_queries = [
        "I'm hiring a software engineer",
        "Compare numerical and verbal tests",
        "Give me personality assessments",
        "How do I use SHL tests?",
        "test"
    ]
    
    print("\n" + "="*80)
    print("      PERFORMANCE BENCHMARK")
    print("="*80)
    
    for query in benchmark_queries:
        start = time.time()
        request = ChatRequest(message=query, history=[])
        await orchestrator.handle_chat(request)
        end = time.time()
        
        print(f"Query: '{query: <35}' | Latency: {(end-start):.2f}s")
        
    summary = PerformanceMonitor.get_summary()
    print("-" * 80)
    print(f"AVERAGE E2E LATENCY: {summary.get('avg_latency_ms', 0):.2f}ms")
    print(f"AVERAGE RETRIEVAL:   {summary.get('avg_retrieval_ms', 0):.2f}ms")
    
    if summary.get('avg_latency_ms', 10000) < 5000:
        print("✅ PERFORMANCE TARGET MET (< 5s)")
    else:
        print("⚠️ PERFORMANCE BELOW TARGET")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
