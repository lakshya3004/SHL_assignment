from typing import List, Tuple
from loguru import logger
from app.models.catalog_models import RawAssessment


class AssessmentFilter:
    """
    Implements strict filtering logic to ensure only 'Individual Test Solutions' 
    are included in the recommender catalog.
    
    Excludes: Pre-packaged Job Solutions, bundles, hiring platforms, and unrelated offerings.
    """

    # Keywords that strongly indicate a bundled solution or non-assessment product
    EXCLUSION_KEYWORDS = [
        "solution", "bundle", "pack", "hiring", "recruitment", "volume", 
        "graduate", "manager", "early career", "platform", "system", 
        "subscription", "license", "consulting", "training", "workshop"
    ]

    # Keywords that strongly indicate an individual assessment
    INCLUSION_SIGNALS = [
        "test", "assessment", "reasoning", "ability", "personality", "skill", 
        "opq", "verify", "motivation", "situational", "judgment", "behavioral",
        "cognitive", "numerical", "verbal", "inductive", "deductive", "calculation",
        "checking", "coding", "language", "mechanical", "spatial"
    ]

    def is_excluded_solution(self, name: str) -> bool:
        """
        Heuristic to identify pre-packaged job solutions or bundles.
        SHL usually suffixes these with 'Solution' or 'Pack'.
        Example: 'Account Manager Solution', 'Graduate Hiring Bundle'.
        """
        name_lower = name.lower()
        
        # 'Solution' is a major red flag for pre-packaged job bundles
        if "solution" in name_lower or "pack" in name_lower:
            return True
            
        # Check for other exclusion keywords
        for kw in self.EXCLUSION_KEYWORDS:
            if kw in name_lower:
                return True
        return False

    def contains_assessment_signals(self, name: str) -> bool:
        """Checks if the name contains signals of being an individual test."""
        name_lower = name.lower()
        return any(signal in name_lower for signal in self.INCLUSION_SIGNALS)

    def is_valid_individual_test(self, raw: RawAssessment) -> Tuple[bool, str]:
        """
        Comprehensive check for validity. 
        Returns (is_valid, reason).
        """
        name = raw.name
        
        # 1. Check for explicit exclusion signals
        if self.is_excluded_solution(name):
            return False, "Identified as a pre-packaged solution or bundle"
            
        # 2. Check for assessment signals (must have at least one)
        if not self.contains_assessment_signals(name):
            return False, "Missing core assessment keywords (unrelated product)"
            
        # 3. Check for malformed data
        if len(name) < 5:
            return False, "Name too short to be a valid assessment"
            
        if not raw.url or "shl.com" not in raw.url:
            return False, "Invalid or external source URL"

        return True, "Valid Individual Test Solution"

    def filter_raw_catalog(self, raw_items: List[RawAssessment]) -> Tuple[List[RawAssessment], List[dict]]:
        """
        Splits raw catalog into accepted items and excluded items for reporting.
        """
        accepted = []
        excluded = []
        
        for item in raw_items:
            is_valid, reason = self.is_valid_individual_test(item)
            if is_valid:
                accepted.append(item)
            else:
                excluded.append({
                    "name": item.name,
                    "url": item.url,
                    "reason": reason
                })
                
        logger.info(f"Filtering complete: {len(accepted)} accepted, {len(excluded)} excluded.")
        return accepted, excluded
