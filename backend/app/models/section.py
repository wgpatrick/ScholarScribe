from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, backref
from uuid import uuid4
from ..db.database import Base

class Section(Base):
    """
    Section model for representing document structure
    """
    __tablename__ = "sections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Section structure
    title = Column(String, nullable=False, index=True)
    level = Column(Integer, nullable=False)  # Heading level (1-6)
    order = Column(Integer, nullable=False)  # For preserving order of sections
    parent_id = Column(UUID(as_uuid=True), ForeignKey("sections.id", ondelete="SET NULL"), nullable=True)
    
    # Content
    content = Column(Text, nullable=True)  # Markdown content of this section
    summary = Column(Text, nullable=True)  # AI-generated summary
    
    # Metadata
    word_count = Column(Integer, nullable=True)
    has_equations = Column(Boolean, default=False)
    has_figures = Column(Boolean, default=False)
    has_tables = Column(Boolean, default=False)
    
    # For keyword extraction and search
    keywords = Column(JSONB, nullable=True)  # Stored as JSON array
    
    # Relationships
    document = relationship("Document", back_populates="sections")
    children = relationship("Section", 
                          backref=backref("parent", remote_side=[id]),
                          cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="section", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="section", cascade="all, delete-orphan")
    annotations = relationship("Annotation", back_populates="section", cascade="all, delete-orphan")
    figures = relationship("Figure", back_populates="section", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Section(id={self.id}, title='{self.title}', level={self.level})>"