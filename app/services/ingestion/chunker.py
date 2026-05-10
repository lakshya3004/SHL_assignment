from typing import List
from loguru import logger
from app.models.catalog_models import ProcessedAssessment, RetrievalDocument


class AssessmentChunker:
    """
    Prepares processed assessment data for vector storage.
    Creates documents that combine semantic information with structured metadata.
    """

    def create_retrieval_documents(self, assessments: List[ProcessedAssessment]) -> List[RetrievalDocument]:
        """
        Transforms assessments into retrieval-friendly documents.
        Optimizes the text field for semantic matching while preserving metadata.
        """
        documents = []
        
        for assessment in assessments:
            # Enhanced text construction for better semantic retrieval (Recall@10 optimization)
            # We explicitly label sections so the LLM/Embeddings understand the context better
            
            # Identify core skills from keywords
            skills = ", ".join(assessment.keywords)
            
            # Structured chunk format
            text_block = (
                f"### ASSESSMENT: {assessment.name}\n"
                f"**Category**: {assessment.test_type}\n"
                f"**Target Skills**: {skills}\n"
                f"**Overview**: {assessment.description}\n"
                f"**Delivery**: {'Remote Supported' if assessment.remote_support else 'Standard'}\n"
                f"**Methodology**: {'Adaptive/IRT' if assessment.adaptive else 'Fixed Form'}\n"
            )
            
            # Metadata for filtering in FAISS
            metadata = {
                "id": assessment.id,
                "name": assessment.name,
                "url": assessment.url,
                "test_type": assessment.test_type,
                "remote_support": assessment.remote_support,
                "quality_score": assessment.quality_score
            }
            
            documents.append(RetrievalDocument(
                assessment_id=assessment.id,
                text=text_block,
                metadata=metadata
            ))
            
        logger.info(f"Created {len(documents)} retrieval documents.")
        return documents

    # TODO: Implement dynamic chunking if descriptions are extremely long ( > 2000 tokens )
    # For SHL assessments, descriptions are typically concise enough for single chunks.
