from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List

from ...db.database import get_db
from ...models.document import Document
from ...services.storage import StorageService
from ...services.pdf_converter import PDFConverterService

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF document and start conversion to markdown
    """
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Initialize services
    storage_service = StorageService()
    
    # Save the PDF
    pdf_path = await storage_service.save_pdf(file)
    
    # Create document record
    document = Document(
        pdf_path=pdf_path,
        title=file.filename.replace(".pdf", ""),  # Simple title from filename
        conversion_status="pending"
    )
    
    # Save to database
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Start background conversion
    converter_service = PDFConverterService()
    background_tasks.add_task(
        converter_service.convert_pdf_to_markdown,
        document.id,
        db
    )
    
    return {
        "id": document.id,
        "uuid": document.uuid,
        "title": document.title,
        "status": document.conversion_status
    }

@router.get("/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get a document by ID
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {
        "id": document.id,
        "uuid": document.uuid,
        "title": document.title,
        "authors": document.authors,
        "conversion_status": document.conversion_status,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
        "markdown_text": document.markdown_text if document.conversion_status == "completed" else None
    }

@router.get("/")
async def list_documents(db: Session = Depends(get_db)):
    """
    List all documents
    """
    documents = db.query(Document).order_by(Document.created_at.desc()).all()
    
    return [
        {
            "id": doc.id,
            "uuid": doc.uuid,
            "title": doc.title,
            "conversion_status": doc.conversion_status,
            "created_at": doc.created_at
        }
        for doc in documents
    ]
