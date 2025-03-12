from sqlalchemy import Column, String, Boolean, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import secrets
from uuid import uuid4
from ..db.database import Base

class AccessLevel(enum.Enum):
    READ_ONLY = "read_only"
    COMMENT = "comment"
    EDIT = "edit"

class ShareLink(Base):
    """
    For sharing documents with others
    """
    __tablename__ = "share_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Access control
    unique_key = Column(String, unique=True, nullable=False, default=lambda: secrets.token_urlsafe(16))
    access_level = Column(Enum(AccessLevel), default=AccessLevel.READ_ONLY)
    
    # Security and tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Usage stats
    view_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Creator info
    created_by = Column(String, nullable=True)  # User ID or API key
    
    # Relationships
    document = relationship("Document", back_populates="share_links")
    
    def __repr__(self):
        return f"<ShareLink(id={self.id}, key='{self.unique_key}', access='{self.access_level.value}')>"