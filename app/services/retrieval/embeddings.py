from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger


class EmbeddingService:
    """
    Handles generation and normalization of text embeddings.
    Uses sentence-transformers/all-MiniLM-L6-v2 for a balance of speed and quality.
    """
    
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self._model = None  # Lazy loading

    @property
    def model(self) -> SentenceTransformer:
        """Lazily load the embedding model to save memory during initialization."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        return self._model

    def embed_text(self, text: str) -> np.ndarray:
        """Generates a single normalized embedding for a string."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return self.normalize_embeddings(embedding.reshape(1, -1))[0]

    def embed_documents(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generates normalized embeddings for a list of strings in batches."""
        logger.info(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.model.encode(
            texts, 
            batch_size=batch_size, 
            show_progress_bar=False, 
            convert_to_numpy=True
        )
        return self.normalize_embeddings(embeddings)

    def normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """
        L2 normalizes embeddings to allow for Cosine Similarity search 
        via Inner Product (IndexFlatIP) in FAISS.
        """
        norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
        # Avoid division by zero
        norm[norm == 0] = 1e-12
        return embeddings / norm
