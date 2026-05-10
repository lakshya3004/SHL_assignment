import sys
import os
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.retrieval.embeddings import EmbeddingService
from app.services.retrieval.vector_store import VectorStore
from app.services.retrieval.keyword_search import KeywordSearchEngine
from app.services.retrieval.hybrid_search import HybridRetriever
from app.services.retrieval.context_builder import RetrievalContextBuilder

def run_test_queries():
    # Initialize services
    embeddings = EmbeddingService()
    v_store = VectorStore()
    k_engine = KeywordSearchEngine()
    
    # Load indices
    if not v_store.load_index() or not k_engine.load():
        logger.error("Failed to load indices. Run build_index.py first.")
        return
        
    retriever = HybridRetriever(v_store, k_engine, embeddings)
    context_builder = RetrievalContextBuilder()
    
    test_queries = [
        "Java backend developer",
        "sales personality assessment",
        "numerical reasoning",
        "leadership hiring",
        "customer support communication"
    ]
    
    print("\n" + "="*80)
    print("      HYBRID RETRIEVAL TEST SUITE")
    print("="*80)
    
    for query in test_queries:
        print(f"\n🔍 QUERY: '{query}'")
        print("-" * 40)
        
        results = retriever.search(query, k=3)
        context = context_builder.build_context(query, results)
        
        for i, res in enumerate(results, 1):
            print(f"{i}. [{res.combined_score:.4f}] {res.name} ({res.test_type})")
        
        if not results:
            print("❌ No results found.")
            
    print("\n" + "="*80)

if __name__ == "__main__":
    run_test_queries()
