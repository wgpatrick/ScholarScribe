from sqlalchemy import Column, String, Text, DateTime, Date, Boolean, Integer, Float, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from uuid import uuid4
from ..db.database import Base

class ProcessingStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(Base):
    """
    Document model for storing academic papers
    """
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    title = Column(String, nullable=True, index=True)
    authors = Column(JSONB, nullable=True)  # Stored as JSON array
    abstract = Column(Text, nullable=True)
    publication_date = Column(Date, nullable=True)
    journal_or_conference = Column(String, nullable=True)
    doi = Column(String, nullable=True)
    
    # Storage
    pdf_path = Column(String, nullable=False)  # S3 key or local path
    pdf_hash = Column(String, nullable=True)   # For uniqueness/integrity checking
    pdf_size = Column(Integer, nullable=True)  # In bytes
    
    # Content
    markdown_content = Column(Text, nullable=True)  # Full markdown content
    raw_text = Column(Text, nullable=True)  # Raw extracted text (optional for search)
    
    # Processing metadata
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    parsing_method = Column(String, nullable=True)  # The method used (LlamaParse, PyMuPDF, etc.)
    parsing_error = Column(Text, nullable=True)  # Store any parsing errors
    processing_time = Column(Float, nullable=True)  # Time taken to process in seconds
    
    # Timestamps and metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_viewed_at = Column(DateTime(timezone=True), nullable=True)
    view_count = Column(Integer, default=0)
    
    # Owner/creator information (for future multi-user support)
    created_by = Column(String, nullable=True)  # User ID or API key
    is_public = Column(Boolean, default=False)  # Whether this document is publicly accessible
    
    # Relationships
    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="document", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="document", cascade="all, delete-orphan")
    annotations = relationship("Annotation", back_populates="document", cascade="all, delete-orphan")
    references = relationship("Reference", back_populates="document", cascade="all, delete-orphan")
    figures = relationship("Figure", back_populates="document", cascade="all, delete-orphan")
    share_links = relationship("ShareLink", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"
