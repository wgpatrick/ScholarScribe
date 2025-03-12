from .document import (
    DocumentBase, 
    DocumentCreate, 
    DocumentUpdate, 
    DocumentResponse,
    DocumentWithSections
)
from .section import (
    SectionBase,
    SectionCreate,
    SectionCreateNested,
    SectionUpdate,
    SectionResponse,
    SectionWithChildren
)
from .reference import (
    ReferenceBase,
    ReferenceCreate,
    ReferenceUpdate,
    ReferenceResponse
)
from .figure import (
    FigureBase,
    FigureCreate,
    FigureUpdate,
    FigureResponse
)

__all__ = [
    # Document schemas
    "DocumentBase", 
    "DocumentCreate", 
    "DocumentUpdate", 
    "DocumentResponse",
    "DocumentWithSections",
    
    # Section schemas
    "SectionBase",
    "SectionCreate",
    "SectionCreateNested",
    "SectionUpdate",
    "SectionResponse",
    "SectionWithChildren",
    
    # Reference schemas
    "ReferenceBase",
    "ReferenceCreate",
    "ReferenceUpdate",
    "ReferenceResponse",
    
    # Figure schemas
    "FigureBase",
    "FigureCreate",
    "FigureUpdate",
    "FigureResponse"
]