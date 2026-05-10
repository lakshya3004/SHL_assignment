import json
import os
from typing import List, Any, Type, TypeVar, Union
from pydantic import BaseModel
from loguru import logger

T = TypeVar("T", bound=BaseModel)

class IngestionStorage:
    """
    Handles persistence of catalog data at different stages of the pipeline.
    Ensures data is saved in structured JSON format within the data/ directory.
    """
    
    @staticmethod
    def save_json(data: Any, file_path: str):
        """Generic JSON save utility."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Convert Pydantic models to dict if necessary
        if isinstance(data, list):
            serializable_data = [
                item.model_dump() if isinstance(item, BaseModel) else item 
                for item in data
            ]
        elif isinstance(data, BaseModel):
            serializable_data = data.model_dump()
        else:
            serializable_data = data
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Saved data to {file_path}")

    @staticmethod
    def load_json(file_path: str, model_type: Optional[Type[T]] = None) -> Union[List[T], Dict[str, Any], List[Dict[str, Any]]]:
        """Generic JSON load utility with optional Pydantic validation."""
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return [] if model_type else {}

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if model_type and isinstance(data, list):
            return [model_type.model_validate(item) for item in data]
        elif model_type and isinstance(data, dict):
            return model_type.model_validate(data)
            
        return data

    @staticmethod
    def get_raw_path() -> str:
        return "data/raw/raw_catalog.json"

    @staticmethod
    def get_processed_path() -> str:
        return "data/processed/processed_catalog.json"

    @staticmethod
    def get_retrieval_path() -> str:
        return "data/processed/retrieval_documents.json"
