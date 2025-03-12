from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4
from datetime import datetime

# Shared properties
class SectionBase(BaseModel):
    """Base Section schema with shared attributes"""
    title: str = Field(..., description="Section title/heading")
    level: int = Field(..., description="Heading level (1-6)")
    content: Optional[str] = Field(None, description="Markdown content of this section")
    order: Optional[int] = Field(None, description="Order in the document or within parent")
    
    # Optional metadata
    summary: Optional[str] = None
    word_count: Optional[int] = None
    has_equations: Optional[bool] = None
    has_figures: Optional[bool] = None
    has_tables: Optional[bool] = None
    keywords: Optional[List[str]] = None

# Properties for section creation
class SectionCreate(SectionBase):
    """Schema for creating a new section"""
    document_id: UUID4 = Field(..., description="Document this section belongs to")
    parent_id: Optional[UUID4] = Field(None, description="Parent section ID if applicable")

# Properties for nested section creation
class SectionCreateNested(SectionBase):
    """Schema for creating a nested section structure"""
    parent_id: Optional[UUID4] = None
    children: Optional[List['SectionCreateNested']] = None

# Self-reference for nested structure
SectionCreateNested.update_forward_refs()

# Properties for section update
class SectionUpdate(BaseModel):
    """Schema for updating an existing section"""
    title: Optional[str] = None
    level: Optional[int] = None
    content: Optional[str] = None
    order: Optional[int] = None
    parent_id: Optional[UUID4] = None
    summary: Optional[str] = None
    word_count: Optional[int] = None
    has_equations: Optional[bool] = None
    has_figures: Optional[bool] = None
    has_tables: Optional[bool] = None
    keywords: Optional[List[str]] = None

# Properties for section response
class SectionResponse(SectionBase):
    """Schema for section response from API"""
    id: UUID4
    document_id: UUID4
    parent_id: Optional[UUID4] = None
    
    class Config:
        from_attributes = True

# Properties for section with children
class SectionWithChildren(SectionResponse):
    """Schema for section with its children"""
    children: List['SectionWithChildren'] = []

# Self-reference for nested response
SectionWithChildren.update_forward_refs()