from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID

from ..repository import BaseRepository
from ...models.document import Document, ProcessingStatus

class DocumentRepository(BaseRepository[Document, Dict[str, Any], Dict[str, Any]]):
    """
    Repository for Document model
    """
    def __init__(self):
        super().__init__(Document)
    
    def get_by_title(self, db: Session, *, title: str) -> Optional[Document]:
        """
        Get a document by title
        """
        return db.query(Document).filter(Document.title == title).first()
    
    def get_by_status(self, db: Session, *, status: ProcessingStatus) -> List[Document]:
        """
        Get documents by processing status
        """
        return db.query(Document).filter(Document.processing_status == status).all()
    
    def update_status(self, db: Session, *, document_id: UUID, status: ProcessingStatus) -> Document:
        """
        Update the processing status of a document
        """
        document = self.get(db, id=document_id)
        if document:
            document.processing_status = status
            db.add(document)
            db.commit()
            db.refresh(document)
        return document
    
    def increment_view_count(self, db: Session, *, document_id: UUID) -> Document:
        """
        Increment the view count for a document
        """
        document = self.get(db, id=document_id)
        if document:
            document.view_count = (document.view_count or 0) + 1
            db.add(document)
            db.commit()
            db.refresh(document)
        return document


# Create a singleton instance
document_repository = DocumentRepository()