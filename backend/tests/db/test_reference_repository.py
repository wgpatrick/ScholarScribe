"""
Integration tests for the reference repository
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.repositories import reference_repository, document_repository
from app.models.document import Document, ProcessingStatus
from app.models.reference import Reference

# Test data
@pytest.fixture
def sample_document_data():
    """Sample document data for testing"""
    return {
        "title": "Test Document",
        "authors": ["Author 1", "Author 2"],
        "pdf_path": "/path/to/test.pdf",
        "processing_status": ProcessingStatus.COMPLETED
    }

@pytest.fixture
def sample_reference_data():
    """Sample reference data for testing"""
    return {
        "raw_citation": "Smith, J. (2020). Test paper. Journal of Testing, 1(2), 123-456.",
        "title": "Test paper",
        "authors": ["Smith, J."],
        "publication_year": 2020,  # Using integer instead of string
        "journal_or_conference": "Journal of Testing",
        "doi": "10.1234/test",
        "url": "https://example.com/paper",
        "order": 1
    }

@pytest.fixture
def sample_references_batch():
    """Multiple reference data samples for batch testing"""
    return [
        {
            "raw_citation": f"Author{i}, A. (202{i}). Paper {i}. Journal {i}, {i}({i}), {i}-{i+10}.",
            "title": f"Paper {i}",
            "authors": [f"Author{i}, A."],
            "publication_year": 2020 + i,  # Using integer instead of string
            "journal_or_conference": f"Journal {i}",
            "order": i
        }
        for i in range(1, 6)  # Create 5 sample references
    ]

@pytest.fixture
def test_document(db_session, sample_document_data):
    """Create a test document in the database"""
    document = document_repository.create(db_session, obj_in=sample_document_data)
    return document

# Test cases
def test_create_reference(db_session, test_document, sample_reference_data):
    """Test creating a reference"""
    # Add document_id to reference data
    reference_data = {**sample_reference_data, "document_id": test_document.id}
    
    # Create the reference
    reference = reference_repository.create(db_session, obj_in=reference_data)
    
    # Check the reference was created with correct data
    assert reference.id is not None
    assert reference.document_id == test_document.id
    assert reference.raw_citation == sample_reference_data["raw_citation"]
    assert reference.title == sample_reference_data["title"]
    assert reference.authors == sample_reference_data["authors"]
    assert reference.publication_year == sample_reference_data["publication_year"]
    assert reference.journal_or_conference == sample_reference_data["journal_or_conference"]
    assert reference.doi == sample_reference_data["doi"]
    assert reference.url == sample_reference_data["url"]
    assert reference.order == sample_reference_data["order"]

def test_create_multiple_references(db_session, test_document, sample_references_batch):
    """Test creating multiple references at once"""
    # Add document_id to each reference
    references_data = [
        {**ref_data, "document_id": test_document.id}
        for ref_data in sample_references_batch
    ]
    
    # Create references in batch
    references = reference_repository.create_multiple(db_session, references_data=references_data)
    
    # Check the references were created
    assert len(references) == len(sample_references_batch)
    
    # Verify their order
    for i, ref in enumerate(references):
        assert ref.order == i + 1

def test_get_reference(db_session, test_document, sample_reference_data):
    """Test retrieving a reference by ID"""
    # Create the reference
    reference_data = {**sample_reference_data, "document_id": test_document.id}
    reference = reference_repository.create(db_session, obj_in=reference_data)
    
    # Retrieve the reference by ID
    retrieved_reference = reference_repository.get(db_session, id=reference.id)
    
    # Check it's the same reference
    assert retrieved_reference is not None
    assert retrieved_reference.id == reference.id
    assert retrieved_reference.raw_citation == reference.raw_citation

def test_get_by_document_id(db_session, test_document, sample_references_batch):
    """Test retrieving all references for a document"""
    # Create multiple references for the document
    references_data = [
        {**ref_data, "document_id": test_document.id}
        for ref_data in sample_references_batch
    ]
    reference_repository.create_multiple(db_session, references_data=references_data)
    
    # Get all references for the document
    references = reference_repository.get_by_document_id(db_session, document_id=test_document.id)
    
    # Check the results
    assert len(references) == len(sample_references_batch)
    
    # Check they're ordered by the 'order' field
    for i, ref in enumerate(references):
        assert ref.order == i + 1

def test_update_reference(db_session, test_document, sample_reference_data):
    """Test updating a reference"""
    # Create the reference
    reference_data = {**sample_reference_data, "document_id": test_document.id}
    reference = reference_repository.create(db_session, obj_in=reference_data)
    
    # Update the reference
    update_data = {
        "title": "Updated Title",
        "journal_or_conference": "Updated Journal",
        "url": "https://example.com/updated"
    }
    
    updated_reference = reference_repository.update(
        db_session, db_obj=reference, obj_in=update_data
    )
    
    # Check the reference was updated
    assert updated_reference.id == reference.id
    assert updated_reference.title == "Updated Title"
    assert updated_reference.journal_or_conference == "Updated Journal"
    assert updated_reference.url == "https://example.com/updated"
    
    # Check that non-updated fields remain the same
    assert updated_reference.raw_citation == reference.raw_citation
    assert updated_reference.authors == reference.authors

def test_delete_reference(db_session, test_document, sample_reference_data):
    """Test deleting a reference"""
    # Create the reference
    reference_data = {**sample_reference_data, "document_id": test_document.id}
    reference = reference_repository.create(db_session, obj_in=reference_data)
    
    # Verify it exists
    assert reference_repository.get(db_session, id=reference.id) is not None
    
    # Delete the reference
    reference_repository.remove(db_session, id=reference.id)
    
    # Verify it's gone
    assert reference_repository.get(db_session, id=reference.id) is None

def test_get_by_doi(db_session, test_document):
    """Test retrieving a reference by DOI"""
    # Create references with DOIs
    references_data = [
        {
            "document_id": test_document.id,
            "raw_citation": "Citation 1",
            "doi": "10.1234/test1",
            "order": 1
        },
        {
            "document_id": test_document.id,
            "raw_citation": "Citation 2",
            "doi": "10.1234/test2",
            "order": 2
        }
    ]
    
    for ref_data in references_data:
        reference_repository.create(db_session, obj_in=ref_data)
    
    # Get reference by DOI
    reference = reference_repository.get_by_doi(db_session, doi="10.1234/test2")
    
    # Check the result
    assert reference is not None
    assert reference.doi == "10.1234/test2"
    assert reference.raw_citation == "Citation 2"