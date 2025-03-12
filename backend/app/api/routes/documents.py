from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ...db.database import get_db
from ...db.repositories import document_repository, section_repository, reference_repository, figure_repository
from ...db.transaction import transaction, run_in_transaction
from ...models.document import ProcessingStatus
from ...models.figure import FigureType
from ...schemas import (
    DocumentCreate, 
    DocumentResponse, 
    DocumentWithSections,
    DocumentUpdate
)
from ...services.storage import storage_service, StorageException
from ...services.document_processor import document_processor

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Upload a PDF document and start conversion to markdown
    
    - **file**: PDF file to upload
    - **title**: Optional title for the document (defaults to filename)
    """
    try:
        # Save the PDF and get metadata
        file_metadata = await storage_service.save_pdf(file)
        
        # Create document data
        document_data = {
            "title": title or file.filename.replace(".pdf", ""),
            "pdf_path": file_metadata["path"],
            "pdf_hash": file_metadata["hash"],
            "pdf_size": file_metadata["size"],
            "processing_status": ProcessingStatus.PENDING
        }
        
        # Create document in database
        document = document_repository.create(db, obj_in=document_data)
        
        # Start background processing
        background_tasks.add_task(
            document_processor.process_document,
            document.id,
            db
        )
        
        return document
        
    except StorageException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save document: {str(e)}"
        )

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: UUID, db: Session = Depends(get_db)):
    """
    Get a document by ID
    
    - **document_id**: UUID of the document
    """
    document = document_repository.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Increment view count
    document_repository.increment_view_count(db, document_id=document_id)
    
    return document

@router.get("/{document_id}/with-sections", response_model=DocumentWithSections)
async def get_document_with_sections(document_id: UUID, db: Session = Depends(get_db)):
    """
    Get a document with all its sections
    
    - **document_id**: UUID of the document
    """
    document = document_repository.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get section tree
    document.sections = section_repository.get_section_tree(db, document_id=document_id)
    
    # Increment view count
    document_repository.increment_view_count(db, document_id=document_id)
    
    return document

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[ProcessingStatus] = None,
    db: Session = Depends(get_db)
):
    """
    List documents with pagination and optional filtering
    
    - **skip**: Number of documents to skip
    - **limit**: Maximum number of documents to return
    - **status**: Filter by processing status
    """
    if status:
        documents = document_repository.get_by_status(db, status=status)
    else:
        documents = document_repository.get_multi(db, skip=skip, limit=limit)
    
    return documents

@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    update_data: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a document
    
    - **document_id**: UUID of the document
    - **update_data**: Data to update
    """
    document = document_repository.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    updated_document = document_repository.update(
        db, db_obj=document, obj_in=update_data.model_dump(exclude_unset=True)
    )
    
    return updated_document

@router.get("/{document_id}/references", response_model=List[dict])
async def get_document_references(document_id: UUID, db: Session = Depends(get_db)):
    """
    Get all references for a document
    
    - **document_id**: UUID of the document
    """
    document = document_repository.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    references = reference_repository.get_by_document_id(db, document_id=document_id)
    
    # Convert to dictionary response
    return [
        {
            "id": ref.id,
            "raw_citation": ref.raw_citation,
            "order": ref.order,
            "title": ref.title,
            "authors": ref.authors,
            "publication_year": ref.publication_year,
            "journal_or_conference": ref.journal_or_conference,
            "doi": ref.doi,
            "url": ref.url
        }
        for ref in references
    ]

@router.get("/{document_id}/figures", response_model=List[dict])
async def get_document_figures(
    document_id: UUID, 
    figure_type: Optional[FigureType] = None,
    db: Session = Depends(get_db)
):
    """
    Get all figures for a document
    
    - **document_id**: UUID of the document
    - **figure_type**: Optional filter by figure type (figure, table, etc.)
    """
    document = document_repository.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if figure_type:
        figures = figure_repository.get_by_type(db, document_id=document_id, figure_type=figure_type)
    else:
        figures = figure_repository.get_by_document_id(db, document_id=document_id)
    
    # Convert to dictionary response
    return [
        {
            "id": fig.id,
            "figure_type": fig.figure_type.value,
            "caption": fig.caption,
            "reference_id": fig.reference_id,
            "content": fig.content if fig.content else None,
            "image_path": fig.image_path,
            "order": fig.order
        }
        for fig in figures
    ]

@router.get("/{document_id}/sections/{section_id}/figures", response_model=List[dict])
async def get_section_figures(document_id: UUID, section_id: UUID, db: Session = Depends(get_db)):
    """
    Get all figures for a specific section
    
    - **document_id**: UUID of the document
    - **section_id**: UUID of the section
    """
    document = document_repository.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    section = section_repository.get(db, id=section_id)
    if not section or section.document_id != document_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    figures = figure_repository.get_by_section_id(db, section_id=section_id)
    
    # Convert to dictionary response
    return [
        {
            "id": fig.id,
            "figure_type": fig.figure_type.value,
            "caption": fig.caption,
            "reference_id": fig.reference_id,
            "content": fig.content if fig.content else None,
            "image_path": fig.image_path,
            "order": fig.order
        }
        for fig in figures
    ]

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a document and its associated file
    
    - **document_id**: UUID of the document
    """
    document = document_repository.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete the file
    pdf_path = document.pdf_path
    file_deleted = await storage_service.delete_file(pdf_path)
    
    # Remove from database (cascade will delete related entities)
    document_repository.remove(db, id=document_id)
    
    return None
