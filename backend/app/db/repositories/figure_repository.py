from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from uuid import UUID

from ..repository import BaseRepository
from ...models.figure import Figure, FigureType

class FigureRepository(BaseRepository[Figure, Dict[str, Any], Dict[str, Any]]):
    """
    Repository for Figure model
    """
    def __init__(self):
        super().__init__(Figure)
    
    def get_by_document_id(self, db: Session, *, document_id: UUID) -> List[Figure]:
        """
        Get all figures for a document, ordered by their order field
        """
        return db.query(Figure)\
            .filter(Figure.document_id == document_id)\
            .order_by(Figure.order)\
            .all()
    
    def get_by_section_id(self, db: Session, *, section_id: UUID) -> List[Figure]:
        """
        Get all figures for a specific section
        """
        return db.query(Figure)\
            .filter(Figure.section_id == section_id)\
            .order_by(Figure.order)\
            .all()
    
    def get_by_reference_id(self, db: Session, *, document_id: UUID, reference_id: str) -> Optional[Figure]:
        """
        Get a figure by its reference ID (e.g., "Figure 1", "Table 3")
        """
        return db.query(Figure)\
            .filter(
                Figure.document_id == document_id,
                Figure.reference_id == reference_id
            )\
            .first()
    
    def get_by_type(self, db: Session, *, document_id: UUID, figure_type: FigureType) -> List[Figure]:
        """
        Get all figures of a specific type for a document
        """
        return db.query(Figure)\
            .filter(
                Figure.document_id == document_id,
                Figure.figure_type == figure_type
            )\
            .order_by(Figure.order)\
            .all()
    
    def search_figures(self, db: Session, *, document_id: UUID, query: str) -> List[Figure]:
        """
        Search figures by caption or reference ID
        """
        return db.query(Figure)\
            .filter(
                Figure.document_id == document_id,
                or_(
                    Figure.caption.ilike(f'%{query}%'),
                    Figure.reference_id.ilike(f'%{query}%')
                )
            )\
            .all()
    
    def update_image_path(self, db: Session, *, figure_id: UUID, image_path: str) -> Optional[Figure]:
        """
        Update the image path for a figure
        """
        figure = self.get(db, id=figure_id)
        if figure:
            figure.image_path = image_path
            db.add(figure)
            db.commit()
            db.refresh(figure)
        return figure
    
    def create_multiple(self, db: Session, *, figures_data: List[Dict[str, Any]]) -> List[Figure]:
        """
        Batch create multiple figures
        """
        figures = []
        for fig_data in figures_data:
            figure = self.model(**fig_data)
            db.add(figure)
            figures.append(figure)
        
        db.commit()
        for fig in figures:
            db.refresh(fig)
        
        return figures


# Create a singleton instance
figure_repository = FigureRepository()