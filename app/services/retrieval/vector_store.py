import faiss
import numpy as np
import os
import json
from typing import List, Dict, Any, Tuple
from loguru import logger

from app.models.retrieval_models import SearchResult


class VectorStore:
    """
    Manages the FAISS vector index for semantic retrieval.
    Maps vector IDs back to assessment metadata.
    """
    
    def __init__(self, index_path: str = "data/vectorstore/faiss.index", metadata_path: str = "data/vectorstore/metadata.json"):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index: Optional[faiss.IndexFlatIP] = None
        self.metadata: List[Dict[str, Any]] = []

    def build_index(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        """
        Creates a new FAISS index from a set of embeddings.
        Expects normalized embeddings for Inner Product (Cosine Similarity).
        """
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype('float32'))
        self.metadata = metadata
        logger.info(f"Built FAISS index with {len(metadata)} documents.")

    def save_index(self):
        """Persists the index and metadata to disk."""
        if self.index is None:
            raise ValueError("No index to save. Build or load an index first.")
            
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved FAISS index to {self.index_path}")

    def load_index(self):
        """Loads index and metadata from disk."""
        if not os.path.exists(self.index_path):
            logger.warning(f"Index file not found: {self.index_path}")
            return False
            
        self.index = faiss.read_index(self.index_path)
        
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
            
        logger.info(f"Loaded FAISS index with {len(self.metadata)} documents.")
        return True

    def search(self, query_embedding: np.ndarray, k: int = 10) -> List[SearchResult]:
        """
        Performs semantic search using vector similarity.
        """
        if self.index is None:
            if not self.load_index():
                return []
                
        # Perform search
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or idx >= len(self.metadata):
                continue
                
            meta = self.metadata[idx]
            results.append(SearchResult(
                assessment_id=meta.get("id", str(idx)),
                name=meta.get("name", "Unknown"),
                score=float(score),
                metadata=meta
            ))
            
        return results
