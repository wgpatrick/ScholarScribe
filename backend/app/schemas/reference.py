from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from enum import Enum

from ..models.reference import MetadataStatus

# Shared properties
class ReferenceBase(BaseModel):
    """Base Reference schema with shared attributes"""
    raw_citation: str = Field(..., description="Original citation text from document")
    order: int = Field(..., description="Order in reference list")
    
    # Parsed data
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    publication_year: Optional[int] = None
    journal_or_conference: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None

# Properties for reference creation
class ReferenceCreate(ReferenceBase):
    """Schema for creating a new reference"""
    document_id: UUID4 = Field(..., description="Document this reference belongs to")
    
    # Optional metadata
    abstract: Optional[str] = None
    citation_count: Optional[int] = None
    appears_in_sections: Optional[List[UUID4]] = None
    citation_contexts: Optional[List[str]] = None
    
    # Status tracking (defaults to NOT_FETCHED)
    metadata_status: Optional[MetadataStatus] = Field(
        default=MetadataStatus.NOT_FETCHED,
        description="Metadata fetching status"
    )

# Properties for reference update
class ReferenceUpdate(BaseModel):
    """Schema for updating an existing reference"""
    raw_citation: Optional[str] = None
    order: Optional[int] = None
    
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    publication_year: Optional[int] = None
    journal_or_conference: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    
    abstract: Optional[str] = None
    citation_count: Optional[int] = None
    appears_in_sections: Optional[List[UUID4]] = None
    citation_contexts: Optional[List[str]] = None
    
    metadata_status: Optional[MetadataStatus] = None
    last_metadata_update: Optional[datetime] = None

# Properties for reference response
class ReferenceResponse(ReferenceBase):
    """Schema for reference response from API"""
    id: UUID4
    document_id: UUID4
    
    abstract: Optional[str] = None
    citation_count: Optional[int] = None
    appears_in_sections: Optional[List[UUID4]] = None
    citation_contexts: Optional[List[str]] = None
    
    metadata_status: MetadataStatus
    last_metadata_update: Optional[datetime] = None
    
    class Config:
        from_attributes = True