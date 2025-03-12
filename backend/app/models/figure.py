from sqlalchemy import Column, String, Text, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from uuid import uuid4
from ..db.database import Base

class FigureType(enum.Enum):
    FIGURE = "figure"
    TABLE = "table"
    EQUATION = "equation"
    CHART = "chart"
    DIAGRAM = "diagram"
    OTHER = "other"

class Figure(Base):
    """
    Represents figures, tables, and other visual elements in the document
    """
    __tablename__ = "figures"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Figure data
    figure_type = Column(Enum(FigureType), default=FigureType.FIGURE)
    caption = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # For tables, could be HTML/markdown representation
    
    # For figures
    image_path = Column(String, nullable=True)  # S3 key or local path for extracted image
    
    # Positioning
    order = Column(Integer, nullable=False)  # Order in document or section
    
    # For search and reference
    reference_id = Column(String, nullable=True)  # E.g., "Figure 1" or "Table 3"
    
    # Relationships
    document = relationship("Document", back_populates="figures")
    section = relationship("Section", back_populates="figures")
    
    def __repr__(self):
        return f"<Figure(id={self.id}, type='{self.figure_type.value}', ref='{self.reference_id}')>"