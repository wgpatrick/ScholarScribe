from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..db.database import Base

class Comment(Base):
    """
    User-created marginal content that appears alongside the document (in the right margin)
    """
    __tablename__ = "comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Comment content
    content = Column(Text, nullable=False)  # Markdown content of the comment
    
    # Positioning
    anchor_text = Column(Text, nullable=False)  # Text to which the comment is anchored
    start_offset = Column(Integer, nullable=False)  # Character offset in the section/document
    end_offset = Column(Integer, nullable=False)  # Character offset end
    
    # Visual styling (minimal)
    color = Column(String, nullable=True)  # For visual distinction if needed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # User tracking (for future multi-user)
    created_by = Column(String, nullable=True)  # User ID or API key
    
    # Relationships
    document = relationship("Document", back_populates="comments")
    section = relationship("Section", back_populates="comments")
    
    def __repr__(self):
        return f"<Comment(id={self.id}, content='{self.content[:30]}...')>"