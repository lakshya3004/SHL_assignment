import sys
import os
import json
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ingestion.storage import IngestionStorage
from app.services.ingestion.quality_checks import QualityChecker
from app.models.catalog_models import ProcessedAssessment

def validate_catalog():
    storage = IngestionStorage()
    processed_path = storage.get_processed_path()
    excluded_path = "data/processed/excluded_catalog_entries.json"
    
    if not os.path.exists(processed_path):
        logger.error(f"Processed catalog not found at {processed_path}. Run run_scraper.py first.")
        return

    logger.info(f"Validating catalog at {processed_path}")
    
    # Load processed data
    with open(processed_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Load excluded data for counts
    excluded_count = 0
    if os.path.exists(excluded_path):
        with open(excluded_path, 'r', encoding='utf-8') as f:
            excluded_count = len(json.load(f))

    # Convert to Pydantic for validation
    assessments = []
    for item in data:
        try:
            assessments.append(ProcessedAssessment.model_validate(item))
        except Exception as e:
            logger.error(f"Schema failure for {item.get('name')}: {e}")

    # Run Quality Checks
    checker = QualityChecker()
    report = checker.run_checks(assessments)
    
    # Save the quality report
    storage.save_json(report, "data/processed/catalog_quality_report.json")

    # Final Summary Output
    print("\n" + "="*50)
    print("      SHL CATALOG VALIDATION SUMMARY")
    print("="*50)
    print(f"Status:              {report['status']}")
    print(f"Total Accepted:      {report['total_count']}")
    print(f"Total Excluded:      {excluded_count}")
    print(f"Average Quality:     {report['average_quality_score']:.2f}/1.00")
    print("-" * 50)
    print("CATEGORY DISTRIBUTION:")
    for cat, count in report['category_distribution'].items():
        print(f" - {cat: <25}: {count}")
    print("-" * 50)
    print("RETRIVAL READINESS:")
    issues = report['issues']
    print(f" - Low Quality Score:  {len(issues['low_quality_score'])}")
    print(f" - Short Descriptions: {len(issues['short_descriptions'])}")
    print(f" - Missing Keywords:   {len(issues['missing_keywords'])}")
    print("="*50 + "\n")
    
    if report['status'] == "PASS":
        logger.success("Catalog is ready for RAG deployment!")
    else:
        logger.warning("Catalog needs refinement before deployment.")

if __name__ == "__main__":
    validate_catalog()
