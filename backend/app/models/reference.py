from sqlalchemy import Column, String, Text, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from uuid import uuid4
from ..db.database import Base

class MetadataStatus(enum.Enum):
    NOT_FETCHED = "not_fetched"
    PENDING = "pending"
    FETCHED = "fetched"
    FAILED = "failed"

class Reference(Base):
    """
    Represents a citation or reference from an academic paper
    """
    __tablename__ = "references"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Citation basics
    raw_citation = Column(Text, nullable=False)  # Original citation text from document
    order = Column(Integer, nullable=False)  # Order in reference list
    
    # Parsed data
    title = Column(String, nullable=True)
    authors = Column(JSONB, nullable=True)  # Stored as JSON array
    publication_year = Column(Integer, nullable=True)
    journal_or_conference = Column(String, nullable=True)
    volume = Column(String, nullable=True)
    issue = Column(String, nullable=True)
    pages = Column(String, nullable=True)
    doi = Column(String, nullable=True, index=True)
    url = Column(String, nullable=True)
    
    # Enhanced metadata (from external APIs)
    abstract = Column(Text, nullable=True)
    citation_count = Column(Integer, nullable=True)
    
    # Citation context
    appears_in_sections = Column(JSONB, nullable=True)  # Sections where cited, as JSON array
    citation_contexts = Column(JSONB, nullable=True)  # Text around citations, as JSON array
    
    # Status tracking
    metadata_status = Column(Enum(MetadataStatus), default=MetadataStatus.NOT_FETCHED)
    last_metadata_update = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="references")
    
    def __repr__(self):
        return f"<Reference(id={self.id}, doi='{self.doi}', title='{self.title[:30] if self.title else None}...')>"