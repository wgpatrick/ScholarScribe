from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from uuid import UUID

from ..repository import BaseRepository
from ...models.reference import Reference, MetadataStatus

class ReferenceRepository(BaseRepository[Reference, Dict[str, Any], Dict[str, Any]]):
    """
    Repository for Reference model
    """
    def __init__(self):
        super().__init__(Reference)
    
    def get_by_document_id(self, db: Session, *, document_id: UUID) -> List[Reference]:
        """
        Get all references for a document, ordered by their order field
        """
        return db.query(Reference)\
            .filter(Reference.document_id == document_id)\
            .order_by(Reference.order)\
            .all()
    
    def get_by_doi(self, db: Session, *, doi: str) -> Optional[Reference]:
        """
        Find a reference by DOI
        """
        return db.query(Reference).filter(Reference.doi == doi).first()
    
    def search_references(self, db: Session, *, document_id: UUID, query: str) -> List[Reference]:
        """
        Search references by title, authors, or raw citation
        """
        return db.query(Reference)\
            .filter(
                Reference.document_id == document_id,
                or_(
                    Reference.title.ilike(f'%{query}%'),
                    Reference.raw_citation.ilike(f'%{query}%'),
                    # This search is a bit more complex for JSONB fields,
                    # we're simplifying by using string containment check
                    func.cast(Reference.authors, 'text').ilike(f'%{query}%')
                )
            )\
            .all()
    
    def get_references_needing_metadata(self, db: Session, *, limit: int = 50) -> List[Reference]:
        """
        Get references that need metadata fetching (not fetched yet or failed)
        """
        return db.query(Reference)\
            .filter(
                Reference.metadata_status.in_([MetadataStatus.NOT_FETCHED, MetadataStatus.FAILED]),
                Reference.doi != None
            )\
            .limit(limit)\
            .all()
    
    def update_metadata_status(
        self, 
        db: Session, 
        *, 
        reference_id: UUID, 
        status: MetadataStatus, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Reference]:
        """
        Update the metadata status and optionally the metadata fields
        """
        reference = self.get(db, id=reference_id)
        if not reference:
            return None
            
        # Update status
        reference.metadata_status = status
        reference.last_metadata_update = func.now()
        
        # If metadata is provided, update reference fields
        if metadata:
            if 'abstract' in metadata:
                reference.abstract = metadata['abstract']
            if 'citation_count' in metadata:
                reference.citation_count = metadata['citation_count']
            if 'title' in metadata and not reference.title:
                reference.title = metadata['title']
            if 'authors' in metadata and not reference.authors:
                reference.authors = metadata['authors']
            if 'journal_or_conference' in metadata and not reference.journal_or_conference:
                reference.journal_or_conference = metadata['journal_or_conference']
            if 'publication_year' in metadata and not reference.publication_year:
                reference.publication_year = metadata['publication_year']
            if 'url' in metadata and not reference.url:
                reference.url = metadata['url']
        
        db.add(reference)
        db.commit()
        db.refresh(reference)
        return reference
    
    def create_multiple(self, db: Session, *, references_data: List[Dict[str, Any]]) -> List[Reference]:
        """
        Batch create multiple references
        """
        references = []
        for ref_data in references_data:
            reference = self.model(**ref_data)
            db.add(reference)
            references.append(reference)
        
        db.commit()
        for ref in references:
            db.refresh(ref)
        
        return references


# Create a singleton instance
reference_repository = ReferenceRepository()