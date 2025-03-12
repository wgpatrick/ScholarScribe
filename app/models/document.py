from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from uuid import uuid4
from ..db.database import Base

class Document(Base):
    """
    Document model for storing academic papers
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=True, index=True)
    authors = Column(String, nullable=True)
    
    # Storage paths
    pdf_path = Column(String, nullable=False)  # Path to the stored PDF
    
    # Document content
    markdown_text = Column(Text, nullable=True)  # Converted markdown content
    conversion_status = Column(String, default="pending")  # pending, processing, completed, failed
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"
