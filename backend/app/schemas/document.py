from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4
from datetime import date, datetime
from enum import Enum

from ..models.document import ProcessingStatus

# Shared properties
class DocumentBase(BaseModel):
    """Base Document schema with shared attributes"""
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    abstract: Optional[str] = None
    publication_date: Optional[date] = None
    journal_or_conference: Optional[str] = None
    doi: Optional[str] = None

# Properties for document creation
class DocumentCreate(DocumentBase):
    """
    Schema for creating a new document
    Note: Some fields like pdf_path, pdf_hash, and pdf_size will be set
    by the upload handler, not provided by the user.
    """
    # Only title is required when creating a document initially
    title: str = Field(..., description="Document title")
    
    # Allow overriding processing status
    processing_status: Optional[ProcessingStatus] = Field(
        default=ProcessingStatus.PENDING,
        description="Processing status"
    )
    
    # Optional metadata that can be provided during creation
    created_by: Optional[str] = Field(
        default=None, 
        description="Creator identifier (API key or user ID)"
    )
    is_public: Optional[bool] = Field(
        default=False, 
        description="Whether the document is publicly accessible"
    )

# Properties for document update
class DocumentUpdate(DocumentBase):
    """Schema for updating an existing document"""
    # All fields are optional for updates
    processing_status: Optional[ProcessingStatus] = None
    parsing_method: Optional[str] = None
    parsing_error: Optional[str] = None
    processing_time: Optional[float] = None
    markdown_content: Optional[str] = None
    raw_text: Optional[str] = None
    is_public: Optional[bool] = None

# Properties for document response
class DocumentResponse(DocumentBase):
    """Schema for document response from API"""
    id: UUID4
    pdf_path: str
    pdf_hash: Optional[str] = None
    pdf_size: Optional[int] = None
    
    processing_status: ProcessingStatus
    parsing_method: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_viewed_at: Optional[datetime] = None
    view_count: int = 0
    
    is_public: bool = False
    
    class Config:
        from_attributes = True

# Properties for document with sections
class DocumentWithSections(DocumentResponse):
    """Schema for document with its sections"""
    sections: List['SectionWithChildren'] = []
    
# Add the forward reference
from .section import SectionWithChildren
DocumentWithSections.update_forward_refs()