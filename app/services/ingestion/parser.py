import re
from typing import List, Optional
from bs4 import BeautifulSoup
from loguru import logger
from app.models.catalog_models import RawAssessment, ProcessedAssessment


class CatalogParser:
    """
    Handles cleaning and normalization of raw scraped assessment data.
    Ensures consistent structure for downstream recommendation and retrieval.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """Removes excessive whitespace, HTML tags, and non-breaking spaces."""
        if not text:
            return ""
        # Remove HTML tags if any left
        text = BeautifulSoup(text, "html.parser").get_text()
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def slugify(text: str) -> str:
        """Creates a unique ID from the assessment name."""
        return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

    def classify_test_type(self, name: str, current_type: str) -> str:
        """Standardizes and improves assessment classification."""
        name_lower = name.lower()
        if "cognitive" in name_lower or any(x in name_lower for x in ["numerical", "verbal", "inductive", "deductive"]):
            return "Cognitive Ability"
        if "personality" in name_lower or "opq" in name_lower:
            return "Personality & Behavioral"
        if "situational" in name_lower or "judgment" in name_lower:
            return "Situational Judgment"
        if "skill" in name_lower or "coding" in name_lower or "language" in name_lower:
            return "Skills & Knowledge"
        
        return current_type or "General Assessment"

    def calculate_initial_quality(self, assessment: ProcessedAssessment) -> float:
        """Calculates a baseline quality score for the processed assessment."""
        score = 1.0
        if not assessment.description or len(assessment.description) < 50:
            score -= 0.4
        if len(assessment.keywords) < 3:
            score -= 0.2
        if assessment.test_type == "General Assessment":
            score -= 0.1
        return max(0.0, score)

    def parse_individual_assessment(self, raw: RawAssessment) -> Optional[ProcessedAssessment]:
        """
        Parses raw assessment data into a ProcessedAssessment model.
        Extracts description from raw_html if present.
        """
        try:
            description = ""
            if raw.raw_html:
                soup = BeautifulSoup(raw.raw_html, "html.parser")
                
                # Enhanced description extraction
                desc_container = soup.select_one(".product-description") or \
                                soup.select_one(".entry-content") or \
                                soup.select_one("main article")
                
                if desc_container:
                    # Remove unwanted elements before cleaning
                    for tag in desc_container.select("script, style, iframe, nav, footer"):
                        tag.decompose()
                    description = self.clean_text(desc_container.get_text())
                else:
                    description = self.clean_text(soup.get_text())[:1500]

            # Normalize metadata and classification
            raw_type = raw.metadata.get("test_type", "")
            test_type = self.classify_test_type(raw.name, raw_type)
            
            # Improved keyword extraction: prioritize meaningful terms
            # Filters out common stop words and small words
            stop_words = {"this", "that", "with", "from", "assessment", "shl", "test"}
            words = re.findall(r'\b[a-z]{4,}\b', raw.name.lower() + " " + test_type.lower())
            keywords = list(set([w for w in words if w not in stop_words]))
            
            processed = ProcessedAssessment(
                id=self.slugify(raw.name),
                name=self.clean_text(raw.name),
                url=raw.url,
                description=description or f"SHL Assessment for {raw.name}",
                test_type=test_type,
                duration=None, 
                remote_support=raw.metadata.get("remote", False),
                adaptive=raw.metadata.get("adaptive", False),
                keywords=keywords,
                source="shl_catalog",
                validation_status="processed"
            )
            
            # Attach quality score
            processed.quality_score = self.calculate_initial_quality(processed)
            
            return processed
        except Exception as e:
            logger.error(f"Failed to parse assessment {raw.name}: {e}")
            return None

    def parse_catalog(self, raw_items: List[RawAssessment]) -> List[ProcessedAssessment]:
        """Processes a list of raw assessments, filtering out duplicates and failures."""
        processed_items = []
        seen_ids = set()
        
        for raw in raw_items:
            processed = self.parse_individual_assessment(raw)
            if processed and processed.id not in seen_ids:
                processed_items.append(processed)
                seen_ids.add(processed.id)
                
        logger.info(f"Parsed {len(processed_items)} valid assessments from {len(raw_items)} raw entries.")
        return processed_items
