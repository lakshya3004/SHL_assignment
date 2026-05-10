import sys
import os
from loguru import logger

# Add project root to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ingestion.scraper import SHLScraper
from app.services.ingestion.parser import CatalogParser
from app.services.ingestion.chunker import AssessmentChunker
from app.services.ingestion.storage import IngestionStorage
from app.services.ingestion.filtering import AssessmentFilter
from app.models.catalog_models import RawAssessment

def main():
    logger.info("Starting SHL Catalog Ingestion Pipeline")
    
    storage = IngestionStorage()
    scraper = SHLScraper()
    parser = CatalogParser()
    chunker = AssessmentChunker()
    filt = AssessmentFilter()
    
    # 1. Scrape
    logger.info("Step 1: Scraping SHL Catalog...")
    raw_data = scraper.run_full_scrape(max_pages=2) 
    storage.save_json(raw_data, storage.get_raw_path())
    
    # 2. Filter
    logger.info("Step 2: Filtering Catalog for Individual Test Solutions...")
    accepted_raw, excluded_raw = filt.filter_raw_catalog(raw_data)
    storage.save_json(excluded_raw, "data/processed/excluded_catalog_entries.json")
    
    # 3. Parse & Normalize
    logger.info("Step 3: Parsing and Normalizing Data...")
    processed_data = parser.parse_catalog(accepted_raw)
    storage.save_json(processed_data, storage.get_processed_path())
    
    # 4. Create Retrieval Documents
    logger.info("Step 4: Creating Retrieval Documents...")
    retrieval_docs = chunker.create_retrieval_documents(processed_data)
    storage.save_json(retrieval_docs, storage.get_retrieval_path())
    
    logger.info("Ingestion pipeline completed successfully!")
    logger.info(f"Raw data: {storage.get_raw_path()}")
    logger.info(f"Processed data: {storage.get_processed_path()}")
    logger.info(f"Retrieval docs: {storage.get_retrieval_path()}")

if __name__ == "__main__":
    main()
