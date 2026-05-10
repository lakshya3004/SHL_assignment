from typing import List, Dict, Any
from loguru import logger

from app.models.retrieval_models import SearchResult, HybridSearchResult
from app.services.retrieval.embeddings import EmbeddingService
from app.services.retrieval.vector_store import VectorStore
from app.services.retrieval.keyword_search import KeywordSearchEngine


class HybridRetriever:
    """
    Orchestrates semantic and keyword search to provide high-recall results.
    Uses Reciprocal Rank Fusion (RRF) to merge and rerank results from both engines.
    """
    
    def __init__(self, vector_store: VectorStore, keyword_engine: KeywordSearchEngine, embedding_service: EmbeddingService):
        self.vector_store = vector_store
        self.keyword_engine = keyword_engine
        self.embedding_service = embedding_service
        self.rrf_k = 60 # Standard constant for RRF

    def search(self, query: str, k: int = 10, semantic_weight: float = 0.7) -> List[HybridSearchResult]:
        """
        Executes hybrid search and returns fused, reranked results.
        """
        logger.info(f"Executing hybrid search for: '{query}'")
        
        # 1. Get semantic results
        query_embedding = self.embedding_service.embed_text(query)
        vector_results = self.vector_store.search(query_embedding, k=k*2)
        
        # 2. Get keyword results
        keyword_results = self.keyword_engine.search(query, k=k*2)
        
        # 3. Reciprocal Rank Fusion
        fused_scores = self.reciprocal_rank_fusion(vector_results, keyword_results)
        
        # 4. Map back to rich models and sort
        combined_results = self._prepare_final_results(fused_scores, vector_results, keyword_results)
        
        # 5. Sort by combined score and return top k
        final_results = sorted(combined_results, key=lambda x: x.combined_score, reverse=True)[:k]
        
        # Assign ranks
        for i, res in enumerate(final_results):
            res.rank = i + 1
            
        logger.info(f"Hybrid search returned {len(final_results)} results.")
        return final_results

    def reciprocal_rank_fusion(self, vector_res: List[SearchResult], keyword_res: List[SearchResult]) -> Dict[str, float]:
        """
        Combines two ranked lists using RRF algorithm.
        Score = sum( 1 / (k + rank) )
        """
        scores = {}
        
        # Process vector results
        for rank, res in enumerate(vector_res, start=1):
            scores[res.assessment_id] = scores.get(res.assessment_id, 0.0) + (1.0 / (self.rrf_k + rank))
            
        # Process keyword results
        for rank, res in enumerate(keyword_res, start=1):
            scores[res.assessment_id] = scores.get(res.assessment_id, 0.0) + (1.0 / (self.rrf_k + rank))
            
        return scores

    def _prepare_final_results(self, fused_scores: Dict[str, float], *results_lists: List[SearchResult]) -> List[HybridSearchResult]:
        """
        Combines metadata from multiple source lists for the final response.
        """
        # Create lookup table for metadata
        id_to_meta = {}
        for r_list in results_lists:
            for item in r_list:
                id_to_meta[item.assessment_id] = item.metadata
        
        final = []
        for aid, score in fused_scores.items():
            meta = id_to_meta[aid]
            final.append(HybridSearchResult(
                assessment_id=aid,
                name=meta.get("name", "Unknown"),
                url=meta.get("url", "#"),
                test_type=meta.get("test_type", "General"),
                description=meta.get("description", ""),
                combined_score=score,
                rank=0 # Placeholder
            ))
        return final
