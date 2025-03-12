"""
Integration tests for the section repository
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.repositories import section_repository, document_repository
from app.models.document import Document, ProcessingStatus
from app.models.section import Section

# Test data
@pytest.fixture
def sample_document_data():
    return {
        "title": "Test Document",
        "authors": ["Author 1", "Author 2"],
        "pdf_path": "/path/to/test.pdf",
        "processing_status": ProcessingStatus.COMPLETED
    }

@pytest.fixture
def sample_sections_data():
    return [
        {
            "title": "Introduction",
            "level": 1,
            "order": 0,
            "content": "This is the introduction content",
            "has_figures": False,
        },
        {
            "title": "Methods",
            "level": 1,
            "order": 1,
            "content": "This is the methods content",
            "has_figures": True,
        },
        {
            "title": "Results",
            "level": 1,
            "order": 2,
            "content": "This is the results content",
            "has_figures": True
        }
    ]

@pytest.fixture
def sample_nested_sections_data():
    return [
        {
            "title": "Introduction",
            "level": 1,
            "order": 0,
            "content": "This is the introduction content",
            "has_figures": False,
            "children": [
                {
                    "title": "Background",
                    "level": 2,
                    "order": 0,
                    "content": "This is the background content",
                    "has_figures": False
                },
                {
                    "title": "Motivation",
                    "level": 2,
                    "order": 1,
                    "content": "This is the motivation content",
                    "has_figures": False
                }
            ]
        },
        {
            "title": "Methods",
            "level": 1,
            "order": 1,
            "content": "This is the methods content",
            "has_figures": True,
            "children": [
                {
                    "title": "Data Collection",
                    "level": 2,
                    "order": 0,
                    "content": "This is the data collection content",
                    "has_figures": False
                }
            ]
        },
        {
            "title": "Results",
            "level": 1,
            "order": 2,
            "content": "This is the results content",
            "has_figures": True
        }
    ]

@pytest.fixture
def test_document(db_session, sample_document_data):
    """Create a test document in the database"""
    document = document_repository.create(db_session, obj_in=sample_document_data)
    return document

# Test cases
def test_create_section(db_session, test_document):
    """Test creating a section"""
    # Create a section
    section_data = {
        "document_id": test_document.id,
        "title": "Test Section",
        "level": 1,
        "order": 0,
        "content": "Test content"
    }
    section = section_repository.create(db_session, obj_in=section_data)
    
    # Assert the section was created correctly
    assert section.title == "Test Section"
    assert section.document_id == test_document.id
    assert section.level == 1
    assert section.content == "Test content"
    
    # Verify we can retrieve it from the database
    retrieved_section = section_repository.get(db_session, id=section.id)
    assert retrieved_section is not None
    assert retrieved_section.id == section.id
    assert retrieved_section.title == "Test Section"

def test_create_multiple_sections(db_session, test_document, sample_sections_data):
    """Test creating multiple sections for a document"""
    # Add document_id to each section
    for section_data in sample_sections_data:
        section_data["document_id"] = test_document.id
    
    # Create multiple sections
    sections = []
    for section_data in sample_sections_data:
        section = section_repository.create(db_session, obj_in=section_data)
        sections.append(section)
    
    # Verify the sections were created
    assert len(sections) == 3
    
    # Get all sections for the document
    document_sections = section_repository.get_by_document_id(db_session, document_id=test_document.id)
    assert len(document_sections) == 3
    
    # Verify the order of sections
    assert document_sections[0].title == "Introduction"
    assert document_sections[1].title == "Methods"
    assert document_sections[2].title == "Results"

def test_create_section_tree(db_session, test_document):
    """Test creating a hierarchical section structure"""
    # Define a simple section tree
    section_tree = [
        {
            "title": "Parent Section",
            "level": 1,
            "content": "Parent content",
            "children": [
                {
                    "title": "Child Section 1",
                    "level": 2,
                    "content": "Child content 1"
                },
                {
                    "title": "Child Section 2",
                    "level": 2,
                    "content": "Child content 2"
                }
            ]
        }
    ]
    
    # Create the parent section
    parent_data = {
        "document_id": test_document.id,
        "title": section_tree[0]["title"],
        "level": section_tree[0]["level"],
        "content": section_tree[0]["content"]
    }
    parent = section_repository.create(db_session, obj_in=parent_data)
    
    # Create the child sections
    children = []
    for i, child_data in enumerate(section_tree[0]["children"]):
        child = section_repository.create(db_session, obj_in={
            "document_id": test_document.id,
            "title": child_data["title"],
            "level": child_data["level"],
            "content": child_data["content"],
            "parent_id": parent.id,
            "order": i
        })
        children.append(child)
    
    # Verify the structure
    # Get the parent section with its children
    parent_with_children = section_repository.get_with_children(db_session, section_id=parent.id)
    assert parent_with_children.title == "Parent Section"
    assert len(parent_with_children.children) == 2
    assert parent_with_children.children[0].title == "Child Section 1"
    assert parent_with_children.children[1].title == "Child Section 2"

def test_get_section_tree(db_session, test_document, sample_nested_sections_data):
    """Test retrieving a complete section tree for a document"""
    # First, create the top-level sections
    top_level_sections = []
    for i, section_data in enumerate(sample_nested_sections_data):
        section = section_repository.create(db_session, obj_in={
            "document_id": test_document.id,
            "title": section_data["title"],
            "level": section_data["level"],
            "content": section_data.get("content", ""),
            "has_figures": section_data.get("has_figures", False),
            "order": i
        })
        top_level_sections.append(section)
    
    # Now add child sections
    for i, parent_data in enumerate(sample_nested_sections_data):
        if "children" in parent_data:
            parent_id = top_level_sections[i].id
            for j, child_data in enumerate(parent_data["children"]):
                section_repository.create(db_session, obj_in={
                    "document_id": test_document.id,
                    "title": child_data["title"],
                    "level": child_data["level"],
                    "content": child_data.get("content", ""),
                    "has_figures": child_data.get("has_figures", False),
                    "parent_id": parent_id,
                    "order": j
                })
    
    # Get the complete section tree
    section_tree = section_repository.get_section_tree(db_session, document_id=test_document.id)
    
    # Verify the structure
    assert len(section_tree) == 3  # 3 top-level sections
    assert section_tree[0].title == "Introduction"
    assert len(section_tree[0].children) == 2
    assert section_tree[0].children[0].title == "Background"
    assert section_tree[0].children[1].title == "Motivation"
    
    assert section_tree[1].title == "Methods"
    assert len(section_tree[1].children) == 1
    assert section_tree[1].children[0].title == "Data Collection"
    
    assert section_tree[2].title == "Results"
    assert len(section_tree[2].children) == 0

def test_update_section(db_session, test_document):
    """Test updating a section"""
    # Create a section
    section_data = {
        "document_id": test_document.id,
        "title": "Original Title",
        "level": 1,
        "content": "Original content"
    }
    section = section_repository.create(db_session, obj_in=section_data)
    
    # Update the section
    update_data = {
        "title": "Updated Title",
        "content": "Updated content"
    }
    updated_section = section_repository.update(
        db_session, 
        db_obj=section,
        obj_in=update_data
    )
    
    # Verify the update
    assert updated_section.id == section.id
    assert updated_section.title == "Updated Title"
    assert updated_section.content == "Updated content"
    assert updated_section.level == 1  # Unchanged

def test_delete_section(db_session, test_document):
    """Test deleting a section"""
    # Create a section
    section_data = {
        "document_id": test_document.id,
        "title": "Section to Delete",
        "level": 1,
    }
    section = section_repository.create(db_session, obj_in=section_data)
    
    # Verify it exists
    assert section_repository.get(db_session, id=section.id) is not None
    
    # Delete the section
    section_repository.remove(db_session, id=section.id)
    
    # Verify it's gone
    assert section_repository.get(db_session, id=section.id) is None

def test_cascade_delete_sections(db_session, test_document):
    """Test that deleting a parent section cascades to children"""
    # Create a parent section
    parent_data = {
        "document_id": test_document.id,
        "title": "Parent Section",
        "level": 1,
    }
    parent = section_repository.create(db_session, obj_in=parent_data)
    
    # Create a child section
    child_data = {
        "document_id": test_document.id,
        "title": "Child Section",
        "level": 2,
        "parent_id": parent.id
    }
    child = section_repository.create(db_session, obj_in=child_data)
    
    # Verify both exist
    assert section_repository.get(db_session, id=parent.id) is not None
    assert section_repository.get(db_session, id=child.id) is not None
    
    # Delete the parent
    section_repository.remove(db_session, id=parent.id)
    
    # Verify both are gone
    assert section_repository.get(db_session, id=parent.id) is None
    assert section_repository.get(db_session, id=child.id) is None