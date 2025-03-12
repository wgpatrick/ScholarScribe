"""
Integration tests for the document repository
"""
import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.repositories import document_repository
from app.models.document import Document, ProcessingStatus

# Test data
@pytest.fixture
def sample_document_data():
    """Sample document data for testing"""
    return {
        "title": "Test Document",
        "authors": ["Author 1", "Author 2"],
        "abstract": "This is a test abstract for the document",
        "publication_date": datetime.now().date(),
        "journal_or_conference": "Test Journal",
        "doi": "10.1234/test.123",
        "pdf_path": "/path/to/test.pdf",
        "pdf_hash": "abcdef123456",
        "pdf_size": 1024,
        "processing_status": ProcessingStatus.PENDING
    }

@pytest.fixture
def sample_documents_batch():
    """Multiple document data samples for batch testing"""
    return [
        {
            "title": f"Test Document {i}",
            "authors": [f"Author {i}"],
            "pdf_path": f"/path/to/test_{i}.pdf",
            "processing_status": ProcessingStatus.PENDING
        }
        for i in range(1, 6)  # Create 5 sample documents
    ]

# Test cases
def test_create_document(db_session, sample_document_data):
    """Test creating a document"""
    # Create the document
    document = document_repository.create(db_session, obj_in=sample_document_data)
    
    # Check the document was created with correct data
    assert document.id is not None
    assert document.title == "Test Document"
    assert document.authors == ["Author 1", "Author 2"]
    assert document.abstract == "This is a test abstract for the document"
    assert document.journal_or_conference == "Test Journal"
    assert document.doi == "10.1234/test.123"
    assert document.pdf_path == "/path/to/test.pdf"
    assert document.pdf_hash == "abcdef123456"
    assert document.pdf_size == 1024
    assert document.processing_status == ProcessingStatus.PENDING
    
    # Check that created_at was set
    assert document.created_at is not None

def test_get_document(db_session, sample_document_data):
    """Test retrieving a document by ID"""
    # Create the document
    document = document_repository.create(db_session, obj_in=sample_document_data)
    
    # Retrieve the document by ID
    retrieved_document = document_repository.get(db_session, id=document.id)
    
    # Check it's the same document
    assert retrieved_document is not None
    assert retrieved_document.id == document.id
    assert retrieved_document.title == document.title

def test_get_multiple_documents(db_session, sample_documents_batch):
    """Test retrieving multiple documents"""
    # Create multiple documents
    created_docs = []
    for doc_data in sample_documents_batch:
        doc = document_repository.create(db_session, obj_in=doc_data)
        created_docs.append(doc)
    
    # Get all documents with pagination
    documents = document_repository.get_multi(db_session, skip=0, limit=10)
    
    # Check the results
    assert len(documents) == len(created_docs)
    
    # Test pagination
    first_page = document_repository.get_multi(db_session, skip=0, limit=2)
    assert len(first_page) == 2
    
    second_page = document_repository.get_multi(db_session, skip=2, limit=2)
    assert len(second_page) == 2
    
    third_page = document_repository.get_multi(db_session, skip=4, limit=2)
    assert len(third_page) == 1  # Only 1 document left

def test_update_document(db_session, sample_document_data):
    """Test updating a document"""
    # Create the document
    document = document_repository.create(db_session, obj_in=sample_document_data)
    
    # Update the document
    update_data = {
        "title": "Updated Title",
        "abstract": "Updated abstract",
        "processing_status": ProcessingStatus.COMPLETED
    }
    
    updated_document = document_repository.update(
        db_session, db_obj=document, obj_in=update_data
    )
    
    # Check the document was updated
    assert updated_document.id == document.id
    assert updated_document.title == "Updated Title"
    assert updated_document.abstract == "Updated abstract"
    assert updated_document.processing_status == ProcessingStatus.COMPLETED
    
    # Check that non-updated fields remain the same
    assert updated_document.authors == document.authors
    assert updated_document.pdf_path == document.pdf_path

def test_update_status(db_session, sample_document_data):
    """Test updating just the processing status"""
    # Create the document
    document = document_repository.create(db_session, obj_in=sample_document_data)
    
    # Update the status using the specialized method
    updated_document = document_repository.update_status(
        db_session, 
        document_id=document.id, 
        status=ProcessingStatus.PROCESSING
    )
    
    # Check the status was updated
    assert updated_document.processing_status == ProcessingStatus.PROCESSING

def test_get_by_status(db_session, sample_documents_batch):
    """Test retrieving documents by status"""
    # Create documents with different statuses
    for i, doc_data in enumerate(sample_documents_batch):
        # Set different statuses
        if i % 2 == 0:
            doc_data["processing_status"] = ProcessingStatus.COMPLETED
        else:
            doc_data["processing_status"] = ProcessingStatus.PROCESSING
        
        document_repository.create(db_session, obj_in=doc_data)
    
    # Get documents by status
    completed_docs = document_repository.get_by_status(db_session, status=ProcessingStatus.COMPLETED)
    processing_docs = document_repository.get_by_status(db_session, status=ProcessingStatus.PROCESSING)
    
    # Check the counts
    assert len(completed_docs) == 3  # 0, 2, 4 are completed
    assert len(processing_docs) == 2  # 1, 3 are processing

def test_delete_document(db_session, sample_document_data):
    """Test deleting a document"""
    # Create the document
    document = document_repository.create(db_session, obj_in=sample_document_data)
    
    # Verify it exists
    assert document_repository.get(db_session, id=document.id) is not None
    
    # Delete the document
    document_repository.remove(db_session, id=document.id)
    
    # Verify it's gone
    assert document_repository.get(db_session, id=document.id) is None

def test_increment_view_count(db_session, sample_document_data):
    """Test incrementing the view count"""
    # Create the document
    document = document_repository.create(db_session, obj_in=sample_document_data)
    assert document.view_count == 0
    
    # Increment view count
    updated_document = document_repository.increment_view_count(db_session, document_id=document.id)
    
    # Check the view count was incremented
    assert updated_document.view_count == 1
    assert updated_document.last_viewed_at is not None
    
    # Increment again
    updated_document = document_repository.increment_view_count(db_session, document_id=document.id)
    assert updated_document.view_count == 2