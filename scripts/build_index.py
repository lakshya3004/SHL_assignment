import sys
import os
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ingestion.storage import IngestionStorage
from app.models.catalog_models import RetrievalDocument
from app.services.retrieval.embeddings import EmbeddingService
from app.services.retrieval.vector_store import VectorStore
from app.services.retrieval.keyword_search import KeywordSearchEngine

def build_retrieval_indices():
    """
    Loads retrieval documents and builds both FAISS and TF-IDF indices.
    """
    logger.info("Initializing Index Build Process")
    
    storage = IngestionStorage()
    embedding_service = EmbeddingService()
    vector_store = VectorStore()
    keyword_engine = KeywordSearchEngine()
    
    # 1. Load Data
    docs_path = storage.get_retrieval_path()
    if not os.path.exists(docs_path):
        logger.error(f"Retrieval documents not found at {docs_path}. Run ingestion first.")
        return
        
    documents: List[RetrievalDocument] = storage.load_json(docs_path, model_type=RetrievalDocument)
    if not documents:
        logger.error("No documents to index.")
        return
        
    texts = [doc.text for doc in documents]
    metadatas = [doc.metadata for doc in documents]
    
    # 2. Build Vector Index
    logger.info("Building Semantic Index (FAISS)...")
    embeddings = embedding_service.embed_documents(texts)
    vector_store.build_index(embeddings, metadatas)
    vector_store.save_index()
    
    # 3. Build Keyword Index
    logger.info("Building Keyword Index (TF-IDF)...")
    keyword_engine.fit(texts, metadatas)
    keyword_engine.save()
    
    logger.success("All retrieval indices built and saved successfully!")

if __name__ == "__main__":
    build_retrieval_indices()
