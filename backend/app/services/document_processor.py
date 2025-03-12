"""
Document Processing Service

This service handles the end-to-end processing of uploaded PDFs:
1. Parsing the PDF to extract structured content
2. Storing the content in the database with proper relationships
3. Tracking progress and handling errors
"""
import logging
import time
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
from sqlalchemy.orm import Session

from ..db.repositories import (
    document_repository, 
    section_repository,
    reference_repository,
    figure_repository
)
from ..db.transaction import transaction, run_in_transaction
from ..models.document import ProcessingStatus
from ..models.figure import FigureType
from .pdf_parsing.llama_parse_client import LlamaParseClient
from .pdf_parsing.structured_extractor import extract_structured_data
from .storage import storage_service

# Configure logging
logger = logging.getLogger(__name__)

class DocumentProcessingService:
    """
    Service for processing documents through the complete pipeline:
    PDF upload → parsing → structured data extraction → database storage
    """
    
    def __init__(self):
        """Initialize the document processor with required clients"""
        self.llama_parse_client = LlamaParseClient()
    
    async def process_document(self, document_id: UUID, db: Session) -> bool:
        """
        Process a document through the full pipeline
        
        Args:
            document_id: UUID of the document to process
            db: Database session
            
        Returns:
            bool: True if processing succeeded, False otherwise
        """
        start_time = time.time()
        
        try:
            # Update document status to processing
            document = document_repository.update_status(
                db, document_id=document_id, status=ProcessingStatus.PROCESSING
            )
            
            if not document:
                logger.error(f"Document not found: {document_id}")
                return False
                
            logger.info(f"Started processing document: {document_id}")
            
            # Get the PDF path
            pdf_path = document.pdf_path
            
            # Process the PDF with LlamaParse and get structured data
            try:
                # Use LlamaParse with structured data extraction
                markdown_content, structured_data = self.llama_parse_client.parse_pdf(
                    pdf_path, return_structured=True
                )
                
                # Store the results using a transaction
                def store_processing_results(db):
                    # 1. Update the document with parsed content
                    logger.info(f"Updating document with parsed content: {document_id}")
                    processing_time = time.time() - start_time
                    
                    doc_update = {
                        "markdown_content": markdown_content,
                        "processing_status": ProcessingStatus.COMPLETED,
                        "processing_time": processing_time,
                        "parsing_method": "LlamaParse",
                    }
                    
                    # Update metadata if available
                    if structured_data.get("title"):
                        doc_update["title"] = structured_data["title"]
                    if structured_data.get("abstract"):
                        doc_update["abstract"] = structured_data["abstract"]
                    if structured_data.get("authors"):
                        doc_update["authors"] = structured_data["authors"]
                    
                    # Update the document
                    document = document_repository.update(
                        db, 
                        db_obj=document_repository.get(db, id=document_id),
                        obj_in=doc_update
                    )
                    
                    # 2. Process sections
                    self._process_sections(db, document_id, structured_data)
                    
                    # 3. Process references
                    self._process_references(db, document_id, structured_data)
                    
                    # 4. Process figures and tables
                    self._process_figures_and_tables(db, document_id, structured_data)
                    
                    return document
                
                # Execute everything in a transaction
                # Don't pass db as it is automatically injected by run_in_transaction
                result = run_in_transaction(store_processing_results)
                
                if result:
                    logger.info(f"Successfully processed document {document_id} in {time.time() - start_time:.2f} seconds")
                    return True
                else:
                    logger.error(f"Failed to store processing results for document {document_id}")
                    return False
                    
            except Exception as e:
                logger.error(f"Error processing document {document_id}: {str(e)}")
                
                # Update document status to failed
                document_repository.update(
                    db, 
                    db_obj=document_repository.get(db, id=document_id),
                    obj_in={
                        "processing_status": ProcessingStatus.FAILED,
                        "parsing_error": str(e)
                    }
                )
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error in document processing: {str(e)}")
            
            # Try to update document status to failed
            try:
                document_repository.update_status(
                    db, document_id=document_id, status=ProcessingStatus.FAILED
                )
            except:
                logger.error(f"Could not update document status for {document_id}")
                
            return False
    
    def _process_sections(self, db: Session, document_id: UUID, structured_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process and store sections from structured data
        
        Args:
            db: Database session
            document_id: UUID of the document
            structured_data: Structured data from the parser
            
        Returns:
            List[Dict]: Processed section data
        """
        logger.info(f"Processing sections for document {document_id}")
        
        # Extract sections
        sections = structured_data.get("sections", [])
        
        if not sections:
            logger.warning(f"No sections found for document {document_id}")
            return []
            
        # Organize sections into a hierarchical structure
        root_sections = []
        section_map = {}
        
        # First pass: create all sections and build a map by title
        for i, section in enumerate(sections):
            # Create section data
            section_data = {
                "document_id": document_id,
                "title": section.get("title", f"Section {i+1}"),
                "level": section.get("level", 1),
                "content": section.get("content", ""),
                "order": i,
                "parent_id": None  # Initially no parent
            }
            
            # Add metadata
            if "word_count" in section:
                section_data["word_count"] = section["word_count"]
            if "has_equations" in section:
                section_data["has_equations"] = section["has_equations"]
            if "has_figures" in section:
                section_data["has_figures"] = section["has_figures"]
            if "has_tables" in section:
                section_data["has_tables"] = section["has_tables"]
            if "keywords" in section:
                section_data["keywords"] = section["keywords"]
                
            # Track for hierarchy building
            section_map[section_data["title"]] = section_data
            
            # Check if it's a root section
            if section_data["level"] == 1:
                root_sections.append(section_data)
                
        # Second pass: establish hierarchical relationships
        # This is a simple heuristic for setting parent-child relationships
        # based on section levels and their order in the document
        last_section_by_level = {}
        
        for section in sections:
            title = section.get("title", "")
            level = section.get("level", 1)
            
            if level > 1 and level - 1 in last_section_by_level:
                # Get the potential parent section
                parent_title = last_section_by_level[level - 1]
                parent_data = section_map.get(parent_title)
                
                if parent_data:
                    # Set parent ID (will be replaced with actual UUID after creation)
                    section_map[title]["parent_id_key"] = parent_title
            
            # Update the last section seen at this level
            last_section_by_level[level] = title
        
        # Create sections in the database
        # We'll do this in a hierarchical way to ensure proper parent-child relationships
        created_sections = []
        section_id_map = {}
        
        # Create root sections first
        for root_section in root_sections:
            section = section_repository.create(db, obj_in=root_section)
            section_id_map[root_section["title"]] = section.id
            created_sections.append(section)
        
        # Now create child sections with proper parent IDs
        for title, section_data in section_map.items():
            # Skip root sections as they've been created
            if section_data["level"] == 1:
                continue
                
            # Set parent ID if applicable
            if "parent_id_key" in section_data:
                parent_title = section_data.pop("parent_id_key")
                if parent_title in section_id_map:
                    section_data["parent_id"] = section_id_map[parent_title]
            
            # Create the section
            section = section_repository.create(db, obj_in=section_data)
            section_id_map[title] = section.id
            created_sections.append(section)
        
        logger.info(f"Created {len(created_sections)} sections for document {document_id}")
        return created_sections

    def _process_references(self, db: Session, document_id: UUID, structured_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process and store references from structured data
        
        Args:
            db: Database session
            document_id: UUID of the document
            structured_data: Structured data from the parser
            
        Returns:
            List[Dict]: Processed reference data
        """
        logger.info(f"Processing references for document {document_id}")
        
        # Extract references
        references = structured_data.get("references", [])
        
        if not references:
            logger.warning(f"No references found for document {document_id}")
            return []
            
        # Process and create references
        reference_data_list = []
        
        for i, ref in enumerate(references):
            if isinstance(ref, str):
                # Simple string reference
                reference_data = {
                    "document_id": document_id,
                    "raw_citation": ref,
                    "order": i
                }
            else:
                # Structured reference
                reference_data = {
                    "document_id": document_id,
                    "raw_citation": ref.get("raw_citation", f"Reference {i+1}"),
                    "order": i,
                    "title": ref.get("title"),
                    "authors": ref.get("authors"),
                    "publication_year": ref.get("year"),
                    "journal_or_conference": ref.get("venue"),
                    "doi": ref.get("doi"),
                    "url": ref.get("url")
                }
            
            reference_data_list.append(reference_data)
        
        # Batch create references
        created_references = reference_repository.create_multiple(db, references_data=reference_data_list)
        
        logger.info(f"Created {len(created_references)} references for document {document_id}")
        return created_references

    def _process_figures_and_tables(self, db: Session, document_id: UUID, structured_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process and store figures and tables from structured data
        
        Args:
            db: Database session
            document_id: UUID of the document
            structured_data: Structured data from the parser
            
        Returns:
            List[Dict]: Processed figure and table data
        """
        logger.info(f"Processing figures and tables for document {document_id}")
        
        # Extract figures and tables
        figures = structured_data.get("figures", [])
        tables = structured_data.get("tables", [])
        
        figure_data_list = []
        
        # Process figures
        for i, fig in enumerate(figures):
            figure_data = {
                "document_id": document_id,
                "figure_type": FigureType.FIGURE,
                "caption": fig.get("caption", f"Figure {i+1}"),
                "reference_id": f"Figure {i+1}",
                "order": i
            }
            
            # Handle image path if available
            if "url" in fig and fig["url"]:
                figure_data["image_path"] = fig["url"]
                
            figure_data_list.append(figure_data)
        
        # Process tables
        for i, table in enumerate(tables):
            table_data = {
                "document_id": document_id,
                "figure_type": FigureType.TABLE,
                "caption": table.get("caption", f"Table {i+1}"),
                "reference_id": f"Table {i+1}",
                "content": table.get("content", ""),
                "order": len(figures) + i  # Tables come after figures in order
            }
            
            figure_data_list.append(table_data)
        
        # Batch create figures and tables
        if figure_data_list:
            created_figures = figure_repository.create_multiple(db, figures_data=figure_data_list)
            logger.info(f"Created {len(created_figures)} figures/tables for document {document_id}")
            return created_figures
        else:
            logger.warning(f"No figures or tables found for document {document_id}")
            return []


# Create a singleton instance
document_processor = DocumentProcessingService()