"""
Integration tests for the figure repository
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.repositories import figure_repository, document_repository, section_repository
from app.models.document import Document, ProcessingStatus
from app.models.figure import Figure, FigureType
from app.models.section import Section

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
def sample_section_data():
    """Sample section data for testing"""
    return {
        "title": "Results",
        "level": 1,
        "content": "This section contains figures and tables.",
        "order": 0  # Add order which is required
    }

@pytest.fixture
def sample_figure_data():
    """Sample figure data for testing"""
    return {
        "figure_type": FigureType.FIGURE,
        "caption": "Figure 1: Test figure showing experimental results",
        "reference_id": "Figure 1",
        "image_path": "/path/to/figure.png",
        "order": 1
    }

@pytest.fixture
def sample_table_data():
    """Sample table data for testing"""
    return {
        "figure_type": FigureType.TABLE,
        "caption": "Table 1: Test table with experimental data",
        "reference_id": "Table 1",
        "content": "| Column 1 | Column 2 |\n|----------|----------|\n| Data 1   | Data 2   |",
        "order": 2
    }

@pytest.fixture
def sample_figures_batch():
    """Multiple figure data samples for batch testing"""
    return [
        {
            "figure_type": FigureType.FIGURE,
            "caption": f"Figure {i}: Test figure {i}",
            "reference_id": f"Figure {i}",
            "image_path": f"/path/to/figure{i}.png",
            "order": i
        }
        for i in range(1, 4)
    ] + [
        {
            "figure_type": FigureType.TABLE,
            "caption": f"Table {i-3}: Test table {i-3}",
            "reference_id": f"Table {i-3}",
            "content": f"Table content {i-3}",
            "order": i
        }
        for i in range(4, 7)
    ]

@pytest.fixture
def test_document(db_session, sample_document_data):
    """Create a test document in the database"""
    document = document_repository.create(db_session, obj_in=sample_document_data)
    return document

@pytest.fixture
def test_section(db_session, test_document, sample_section_data):
    """Create a test section in the database"""
    section_data = {**sample_section_data, "document_id": test_document.id}
    section = section_repository.create(db_session, obj_in=section_data)
    return section

# Test cases
def test_create_figure(db_session, test_document, sample_figure_data):
    """Test creating a figure"""
    # Add document_id to figure data
    figure_data = {**sample_figure_data, "document_id": test_document.id}
    
    # Create the figure
    figure = figure_repository.create(db_session, obj_in=figure_data)
    
    # Check the figure was created with correct data
    assert figure.id is not None
    assert figure.document_id == test_document.id
    assert figure.figure_type == FigureType.FIGURE
    assert figure.caption == sample_figure_data["caption"]
    assert figure.reference_id == sample_figure_data["reference_id"]
    assert figure.image_path == sample_figure_data["image_path"]
    assert figure.order == sample_figure_data["order"]

def test_create_table(db_session, test_document, sample_table_data):
    """Test creating a table"""
    # Add document_id to table data
    table_data = {**sample_table_data, "document_id": test_document.id}
    
    # Create the table
    table = figure_repository.create(db_session, obj_in=table_data)
    
    # Check the table was created with correct data
    assert table.id is not None
    assert table.document_id == test_document.id
    assert table.figure_type == FigureType.TABLE
    assert table.caption == sample_table_data["caption"]
    assert table.reference_id == sample_table_data["reference_id"]
    assert table.content == sample_table_data["content"]
    assert table.order == sample_table_data["order"]

def test_create_multiple_figures(db_session, test_document, sample_figures_batch):
    """Test creating multiple figures at once"""
    # Add document_id to each figure
    figures_data = [
        {**fig_data, "document_id": test_document.id}
        for fig_data in sample_figures_batch
    ]
    
    # Create figures in batch
    figures = figure_repository.create_multiple(db_session, figures_data=figures_data)
    
    # Check the figures were created
    assert len(figures) == len(sample_figures_batch)
    
    # Check figures and tables were created correctly
    figures_count = sum(1 for fig in figures if fig.figure_type == FigureType.FIGURE)
    tables_count = sum(1 for fig in figures if fig.figure_type == FigureType.TABLE)
    
    assert figures_count == 3
    assert tables_count == 3

def test_get_figure(db_session, test_document, sample_figure_data):
    """Test retrieving a figure by ID"""
    # Create the figure
    figure_data = {**sample_figure_data, "document_id": test_document.id}
    figure = figure_repository.create(db_session, obj_in=figure_data)
    
    # Retrieve the figure by ID
    retrieved_figure = figure_repository.get(db_session, id=figure.id)
    
    # Check it's the same figure
    assert retrieved_figure is not None
    assert retrieved_figure.id == figure.id
    assert retrieved_figure.caption == figure.caption

def test_get_by_document_id(db_session, test_document, sample_figures_batch):
    """Test retrieving all figures for a document"""
    # Create multiple figures for the document
    figures_data = [
        {**fig_data, "document_id": test_document.id}
        for fig_data in sample_figures_batch
    ]
    figure_repository.create_multiple(db_session, figures_data=figures_data)
    
    # Get all figures for the document
    figures = figure_repository.get_by_document_id(db_session, document_id=test_document.id)
    
    # Check the results
    assert len(figures) == len(sample_figures_batch)
    
    # Check they're ordered by the 'order' field
    for i, fig in enumerate(figures):
        assert fig.order == i + 1

def test_get_by_type(db_session, test_document, sample_figures_batch):
    """Test retrieving figures by type"""
    # Create multiple figures and tables for the document
    figures_data = [
        {**fig_data, "document_id": test_document.id}
        for fig_data in sample_figures_batch
    ]
    figure_repository.create_multiple(db_session, figures_data=figures_data)
    
    # Get figures by type
    figures = figure_repository.get_by_type(
        db_session, document_id=test_document.id, figure_type=FigureType.FIGURE
    )
    
    tables = figure_repository.get_by_type(
        db_session, document_id=test_document.id, figure_type=FigureType.TABLE
    )
    
    # Check the results
    assert len(figures) == 3
    assert len(tables) == 3
    
    # Verify they are the right types
    for fig in figures:
        assert fig.figure_type == FigureType.FIGURE
    
    for table in tables:
        assert table.figure_type == FigureType.TABLE

def test_get_by_section_id(db_session, test_document, test_section, sample_figures_batch):
    """Test retrieving figures for a specific section"""
    # Create figures linked to the section
    figures_data = [
        {**fig_data, "document_id": test_document.id, "section_id": test_section.id}
        for fig_data in sample_figures_batch[:3]  # Just add 3 figures to the section
    ]
    
    # Create some figures not linked to this section
    other_figures_data = [
        {**fig_data, "document_id": test_document.id}
        for fig_data in sample_figures_batch[3:]  # These 3 aren't linked to the section
    ]
    
    # Create both sets of figures
    figure_repository.create_multiple(db_session, figures_data=figures_data)
    figure_repository.create_multiple(db_session, figures_data=other_figures_data)
    
    # Get figures for the section
    section_figures = figure_repository.get_by_section_id(db_session, section_id=test_section.id)
    
    # Check the results
    assert len(section_figures) == 3

def test_update_figure(db_session, test_document, sample_figure_data):
    """Test updating a figure"""
    # Create the figure
    figure_data = {**sample_figure_data, "document_id": test_document.id}
    figure = figure_repository.create(db_session, obj_in=figure_data)
    
    # Update the figure
    update_data = {
        "caption": "Updated Caption",
        "image_path": "/path/to/updated.png"
    }
    
    updated_figure = figure_repository.update(
        db_session, db_obj=figure, obj_in=update_data
    )
    
    # Check the figure was updated
    assert updated_figure.id == figure.id
    assert updated_figure.caption == "Updated Caption"
    assert updated_figure.image_path == "/path/to/updated.png"
    
    # Check that non-updated fields remain the same
    assert updated_figure.figure_type == figure.figure_type
    assert updated_figure.reference_id == figure.reference_id

def test_delete_figure(db_session, test_document, sample_figure_data):
    """Test deleting a figure"""
    # Create the figure
    figure_data = {**sample_figure_data, "document_id": test_document.id}
    figure = figure_repository.create(db_session, obj_in=figure_data)
    
    # Verify it exists
    assert figure_repository.get(db_session, id=figure.id) is not None
    
    # Delete the figure
    figure_repository.remove(db_session, id=figure.id)
    
    # Verify it's gone
    assert figure_repository.get(db_session, id=figure.id) is None