from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from uuid import UUID

from ..repository import BaseRepository
from ...models.section import Section

class SectionRepository(BaseRepository[Section, Dict[str, Any], Dict[str, Any]]):
    """
    Repository for Section model with hierarchical query support
    """
    def __init__(self):
        super().__init__(Section)
    
    def get_by_document_id(self, db: Session, *, document_id: UUID) -> List[Section]:
        """
        Get all sections for a document
        """
        return db.query(Section).filter(Section.document_id == document_id).all()
    
    def get_root_sections(self, db: Session, *, document_id: UUID) -> List[Section]:
        """
        Get top-level sections (no parent) for a document
        """
        return db.query(Section)\
            .filter(
                Section.document_id == document_id,
                Section.parent_id == None
            )\
            .order_by(Section.order)\
            .all()
    
    def get_section_with_children(self, db: Session, *, section_id: UUID) -> Optional[Section]:
        """
        Get a section including its immediate children
        """
        return db.query(Section)\
            .options(joinedload(Section.children))\
            .filter(Section.id == section_id)\
            .first()
    
    def get_section_tree(self, db: Session, *, document_id: UUID) -> List[Section]:
        """
        Get the complete section tree for a document
        Returns all top-level sections with their children pre-loaded.
        """
        from sqlalchemy.orm import joinedload
        
        # Get all sections ordered by their order field
        all_sections = db.query(Section)\
            .filter(Section.document_id == document_id)\
            .order_by(Section.order)\
            .all()
        
        # Get the root sections (no parent)
        root_sections = [s for s in all_sections if s.parent_id is None]
        
        # Create a dictionary of children by parent_id
        children_by_parent = {}
        for section in all_sections:
            if section.parent_id:
                if section.parent_id not in children_by_parent:
                    children_by_parent[section.parent_id] = []
                children_by_parent[section.parent_id].append(section)
        
        # Build the tree manually
        def add_children(section):
            if section.id in children_by_parent:
                section.children = sorted(children_by_parent[section.id], key=lambda s: s.order)
                for child in section.children:
                    add_children(child)
        
        # Add children to root sections
        for section in root_sections:
            add_children(section)
        
        return root_sections
    
    def create_section_tree(self, db: Session, *, document_id: UUID, sections_data: List[Dict[str, Any]]) -> List[Section]:
        """
        Create a hierarchical tree of sections for a document
        
        Expects a list of section data dictionaries with optional 'children' key
        containing nested sections.
        """
        created_sections = []
        
        # Process sections recursively
        def process_sections(sections_list, parent_id=None, order_start=0):
            created = []
            for i, section_data in enumerate(sections_list):
                # Create a copy of the data without children
                section_dict = section_data.copy()
                children = section_dict.pop('children', [])
                
                # Set parent_id and order
                section_dict['document_id'] = document_id
                section_dict['parent_id'] = parent_id
                section_dict['order'] = order_start + i
                
                # Create the section
                section = self.create(db, obj_in=section_dict)
                created.append(section)
                
                # Process children recursively
                if children:
                    child_sections = process_sections(children, section.id, 0)
                    created.extend(child_sections)
            
            return created
        
        # Start with top-level sections (no parent)
        created_sections = process_sections(sections_data)
        db.commit()
        
        return created_sections
    
    def update_section_order(self, db: Session, *, section_ids: List[UUID], parent_id: Optional[UUID] = None) -> List[Section]:
        """
        Update the order of sections under the same parent
        """
        updated_sections = []
        
        # Check that all sections exist and have the same parent
        for i, section_id in enumerate(section_ids):
            section = self.get(db, id=section_id)
            if section and section.parent_id == parent_id:
                section.order = i
                db.add(section)
                updated_sections.append(section)
        
        db.commit()
        return updated_sections
    
    def move_section(self, db: Session, *, section_id: UUID, new_parent_id: Optional[UUID], new_order: int) -> Optional[Section]:
        """
        Move a section to a new parent and/or position
        """
        section = self.get(db, id=section_id)
        if not section:
            return None
            
        # Validate new parent is not the section itself or its descendant
        if new_parent_id:
            parent = self.get(db, id=new_parent_id)
            if not parent:
                return None
                
            # Check if new_parent_id is a descendant of section_id
            current_id = parent.parent_id
            while current_id:
                if current_id == section_id:
                    # Circular reference detected
                    return None
                    
                parent_section = self.get(db, id=current_id)
                if not parent_section:
                    break
                current_id = parent_section.parent_id
        
        # Execute move
        old_parent_id = section.parent_id
        section.parent_id = new_parent_id
        section.order = new_order
        
        # Reorder siblings at old location
        if old_parent_id is not None:
            old_siblings = db.query(Section)\
                .filter(
                    Section.parent_id == old_parent_id,
                    Section.id != section_id
                )\
                .order_by(Section.order)\
                .all()
                
            for i, sibling in enumerate(old_siblings):
                sibling.order = i
                db.add(sibling)
        
        # Reorder siblings at new location
        if new_parent_id is not None:
            new_siblings = db.query(Section)\
                .filter(
                    Section.parent_id == new_parent_id,
                    Section.id != section_id
                )\
                .order_by(Section.order)\
                .all()
                
            for i, sibling in enumerate(new_siblings):
                if i >= new_order:
                    sibling.order = i + 1
                    db.add(sibling)
        
        db.add(section)
        db.commit()
        db.refresh(section)
        return section
    
    def search_sections(self, db: Session, *, document_id: UUID, query: str, limit: int = 20) -> List[Section]:
        """
        Search for sections by title or content
        """
        return db.query(Section)\
            .filter(
                Section.document_id == document_id,
                or_(
                    Section.title.ilike(f'%{query}%'),
                    Section.content.ilike(f'%{query}%')
                )
            )\
            .limit(limit)\
            .all()
    
    def get_sections_with_figures(self, db: Session, *, document_id: UUID) -> List[Section]:
        """
        Get sections that contain figures
        """
        return db.query(Section)\
            .filter(
                Section.document_id == document_id,
                Section.has_figures == True
            )\
            .all()
    
    def get_section_with_context(self, db: Session, *, section_id: UUID) -> Tuple[Optional[Section], Optional[Section], List[Section]]:
        """
        Get a section with its parent and siblings
        Returns tuple of (section, parent, siblings)
        """
        section = self.get(db, id=section_id)
        if not section:
            return None, None, []
            
        parent = None
        siblings = []
        
        if section.parent_id:
            parent = self.get(db, id=section.parent_id)
            siblings = db.query(Section)\
                .filter(
                    Section.parent_id == section.parent_id,
                    Section.id != section_id
                )\
                .order_by(Section.order)\
                .all()
        else:
            # Get other root sections as siblings
            siblings = db.query(Section)\
                .filter(
                    Section.document_id == section.document_id,
                    Section.parent_id == None,
                    Section.id != section_id
                )\
                .order_by(Section.order)\
                .all()
                
        return section, parent, siblings


# Create a singleton instance
section_repository = SectionRepository()