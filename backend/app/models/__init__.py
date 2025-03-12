from .document import Document, ProcessingStatus
from .section import Section
from .note import Note
from .comment import Comment
from .annotation import Annotation, AnnotationType
from .reference import Reference, MetadataStatus
from .figure import Figure, FigureType
from .sharelink import ShareLink, AccessLevel

# Import all models to ensure they are registered with SQLAlchemy
__all__ = [
    "Document", 
    "ProcessingStatus",
    "Section",
    "Note",
    "Comment",
    "Annotation",
    "AnnotationType",
    "Reference",
    "MetadataStatus",
    "Figure",
    "FigureType",
    "ShareLink",
    "AccessLevel"
]