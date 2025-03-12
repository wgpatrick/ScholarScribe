from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..db.database import Base

class Note(Base):
    """
    Inline user-generated content that blends directly with the document text
    """
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Note content
    content = Column(Text, nullable=False)  # Markdown content of the inline note
    
    # Positioning
    start_offset = Column(Integer, nullable=False)  # Character offset in the section/document
    end_offset = Column(Integer, nullable=False)  # Character offset end
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # User tracking (for future multi-user)
    created_by = Column(String, nullable=True)  # User ID or API key
    
    # Relationships
    document = relationship("Document", back_populates="notes")
    section = relationship("Section", back_populates="notes")
    
    def __repr__(self):
        return f"<Note(id={self.id}, content='{self.content[:30]}...')>"