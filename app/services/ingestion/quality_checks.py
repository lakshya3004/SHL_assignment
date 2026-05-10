from typing import List, Dict, Any
from loguru import logger
from app.models.catalog_models import ProcessedAssessment


class QualityChecker:
    """
    Performs post-processing quality checks on the assessment catalog.
    Detects duplicates, weak descriptions, and generates quality metrics.
    """

    def run_checks(self, assessments: List[ProcessedAssessment]) -> Dict[str, Any]:
        """
        Runs a suite of quality checks and returns a summary report.
        """
        report = {
            "total_count": len(assessments),
            "average_quality_score": 0.0,
            "category_distribution": {},
            "issues": {
                "short_descriptions": [],
                "missing_keywords": [],
                "low_quality_score": [],
                "suspicious_urls": []
            },
            "status": "PASS"
        }

        if not assessments:
            report["status"] = "FAIL (Empty Catalog)"
            return report

        total_score = 0.0
        
        for item in assessments:
            total_score += item.quality_score
            
            # Category distribution
            cat = item.test_type
            report["category_distribution"][cat] = report["category_distribution"].get(cat, 0) + 1
            
            # Issue detection
            if len(item.description) < 100:
                report["issues"]["short_descriptions"].append(item.id)
                
            if not item.keywords:
                report["issues"]["missing_keywords"].append(item.id)
                
            if item.quality_score < 0.5:
                report["issues"]["low_quality_score"].append(item.id)
                
            if "shl.com" not in item.url:
                report["issues"]["suspicious_urls"].append(item.id)

        report["average_quality_score"] = total_score / len(assessments)
        
        # Determine overall status
        if report["average_quality_score"] < 0.6:
            report["status"] = "WARNING (Low Average Quality)"
            
        logger.info(f"Quality check completed. Avg Score: {report['average_quality_score']:.2f}")
        return report
