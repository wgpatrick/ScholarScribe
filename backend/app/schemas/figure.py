from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from enum import Enum

from ..models.figure import FigureType

# Shared properties
class FigureBase(BaseModel):
    """Base Figure schema with shared attributes"""
    figure_type: FigureType = Field(..., description="Type of figure (figure, table, equation, etc.)")
    caption: Optional[str] = Field(None, description="Figure caption")
    reference_id: Optional[str] = Field(None, description="Reference ID (e.g., 'Figure 1')")
    content: Optional[str] = Field(
        None, 
        description="Content of the figure (e.g., HTML/markdown for tables)"
    )
    order: int = Field(..., description="Order in document or section")

# Properties for figure creation
class FigureCreate(FigureBase):
    """Schema for creating a new figure"""
    document_id: UUID4 = Field(..., description="Document this figure belongs to")
    section_id: Optional[UUID4] = Field(None, description="Section this figure belongs to (if applicable)")
    image_path: Optional[str] = Field(None, description="Path to the figure image if applicable")

# Properties for figure update
class FigureUpdate(BaseModel):
    """Schema for updating an existing figure"""
    figure_type: Optional[FigureType] = None
    caption: Optional[str] = None
    reference_id: Optional[str] = None
    content: Optional[str] = None
    image_path: Optional[str] = None
    order: Optional[int] = None
    section_id: Optional[UUID4] = None

# Properties for figure response
class FigureResponse(FigureBase):
    """Schema for figure response from API"""
    id: UUID4
    document_id: UUID4
    section_id: Optional[UUID4] = None
    image_path: Optional[str] = None
    
    class Config:
        from_attributes = True