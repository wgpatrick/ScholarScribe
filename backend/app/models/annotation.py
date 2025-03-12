from sqlalchemy import Column, String, Text, Integer, Float, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from uuid import uuid4
from ..db.database import Base

class AnnotationType(enum.Enum):
    DEFINITION = "definition"
    EXPLANATION = "explanation"
    CONTEXT = "context"
    SUMMARY = "summary"
    OTHER = "other"

class Annotation(Base):
    """
    LLM-generated marginal content for definitions and explanations (also in the right margin)
    """
    __tablename__ = "annotations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Annotation content
    text = Column(Text, nullable=False)  # The text being annotated
    annotation_text = Column(Text, nullable=False)  # The LLM-generated definition/explanation
    annotation_type = Column(Enum(AnnotationType), default=AnnotationType.DEFINITION)
    
    # Positioning
    start_offset = Column(Integer, nullable=False)  # Character offset in the section/document
    end_offset = Column(Integer, nullable=False)  # Character offset end
    
    # LLM metadata
    model_used = Column(String, nullable=True)  # Which LLM generated this annotation
    confidence_score = Column(Float, nullable=True)  # If applicable
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="annotations")
    section = relationship("Section", back_populates="annotations")
    
    def __repr__(self):
        return f"<Annotation(id={self.id}, type='{self.annotation_type.value}', text='{self.text[:30]}...')>"