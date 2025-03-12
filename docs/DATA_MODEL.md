# ScholarScribe Data Model

This document outlines the database schema and data model for the ScholarScribe application.

## Overview

ScholarScribe uses a relational database (PostgreSQL) to store documents, their parsed content, and user interactions. The data model is designed to support academic paper reading, annotation, and note-taking workflows.

## Core Entities

### 1. Document

The central entity representing an academic paper or document.

```python
class Document:
    id: UUID  # Primary key
    title: str
    authors: List[str]  # Stored as JSON array
    abstract: str
    publication_date: Optional[date]
    journal_or_conference: Optional[str]
    doi: Optional[str]  # Document DOI if available
    
    # Storage
    pdf_path: str  # S3 key or local path
    pdf_hash: str  # For uniqueness/integrity checking
    pdf_size: int  # In bytes
    
    # Content
    markdown_content: str  # Full markdown content
    raw_text: Optional[str]  # Raw extracted text (optional for search)
    
    # Processing metadata
    processing_status: Enum  # pending, processing, completed, failed
    parsing_method: str  # The method used (LlamaParse, PyMuPDF, etc.)
    parsing_error: Optional[str]  # Store any parsing errors
    processing_time: float  # Time taken to process in seconds
    
    # Timestamps and metadata
    created_at: datetime
    updated_at: datetime
    last_viewed_at: datetime
    view_count: int
    
    # Owner/creator information (for future multi-user support)
    created_by: Optional[str]  # User ID or API key
    is_public: bool  # Whether this document is publicly accessible
```

### 2. Section

Represents a section of a document, maintaining document structure.

```python
class Section:
    id: UUID  # Primary key
    document_id: UUID  # Foreign key to Document
    
    # Section structure
    title: str  # Section heading
    level: int  # Heading level (1-6)
    order: int  # For preserving order of sections
    parent_id: Optional[UUID]  # For hierarchical sections (self-reference)
    
    # Content
    content: str  # Markdown content of this section
    summary: Optional[str]  # AI-generated summary
    
    # Metadata
    word_count: int
    has_equations: bool
    has_figures: bool
    has_tables: bool
    
    # For keyword extraction and search
    keywords: List[str]  # Stored as JSON array
```

### 3. Note

Inline user-generated content that blends directly with the document text (like in Notion).

```python
class Note:
    id: UUID  # Primary key
    document_id: UUID  # Foreign key to Document
    section_id: Optional[UUID]  # Foreign key to Section (if applicable)
    
    # Note content
    content: str  # Markdown content of the inline note
    
    # Positioning
    start_offset: int  # Character offset in the section/document
    end_offset: int  # Character offset end
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # User tracking (for future multi-user)
    created_by: Optional[str]  # User ID or API key
```

### 4. Comment

User-created marginal content that appears alongside the document (in the right margin).

```python
class Comment:
    id: UUID  # Primary key
    document_id: UUID  # Foreign key to Document
    section_id: Optional[UUID]  # Foreign key to Section (if applicable)
    
    # Comment content
    content: str  # Markdown content of the comment
    
    # Positioning
    anchor_text: str  # Text to which the comment is anchored
    start_offset: int  # Character offset in the section/document
    end_offset: int  # Character offset end
    
    # Visual styling (minimal)
    color: Optional[str]  # For visual distinction if needed
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # User tracking (for future multi-user)
    created_by: Optional[str]  # User ID or API key
```

### 5. Annotation

LLM-generated marginal content for definitions and explanations (also in the right margin).

```python
class Annotation:
    id: UUID  # Primary key
    document_id: UUID  # Foreign key to Document
    section_id: Optional[UUID]  # Foreign key to Section (if applicable)
    
    # Annotation content
    text: str  # The text being annotated
    annotation_text: str  # The LLM-generated definition/explanation
    annotation_type: Enum  # definition, explanation, context, etc.
    
    # Positioning
    start_offset: int  # Character offset in the section/document
    end_offset: int  # Character offset end
    
    # LLM metadata
    model_used: str  # Which LLM generated this annotation
    confidence_score: Optional[float]  # If applicable
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### 6. Reference

Represents a citation or reference from the academic paper.

```python
class Reference:
    id: UUID  # Primary key
    document_id: UUID  # Foreign key to Document
    
    # Citation basics
    raw_citation: str  # Original citation text from document
    order: int  # Order in reference list
    
    # Parsed data
    title: Optional[str]
    authors: List[str]  # Stored as JSON array
    publication_year: Optional[int]
    journal_or_conference: Optional[str]
    volume: Optional[str]
    issue: Optional[str]
    pages: Optional[str]
    doi: Optional[str]
    url: Optional[str]
    
    # Enhanced metadata (from external APIs)
    abstract: Optional[str]
    citation_count: Optional[int]
    
    # Citation context
    appears_in_sections: List[UUID]  # Sections where cited, as JSON array
    citation_contexts: List[str]  # Text around citations, as JSON array
    
    # Status tracking
    metadata_status: Enum  # not_fetched, pending, fetched, failed
    last_metadata_update: Optional[datetime]
```

### 7. Figure

Represents figures, tables, and other visual elements in the document.

```python
class Figure:
    id: UUID  # Primary key
    document_id: UUID  # Foreign key to Document
    section_id: Optional[UUID]  # Foreign key to Section (if applicable)
    
    # Figure data
    figure_type: Enum  # figure, table, equation, etc.
    caption: str
    content: str  # For tables, could be HTML/markdown representation
    
    # For figures
    image_path: Optional[str]  # S3 key or local path for extracted image
    
    # Positioning
    order: int  # Order in document or section
    
    # For search and reference
    reference_id: str  # E.g., "Figure 1" or "Table 3"
```

### 8. ShareLink

For sharing documents with others.

```python
class ShareLink:
    id: UUID  # Primary key
    document_id: UUID  # Foreign key to Document
    
    # Access control
    unique_key: str  # Random generated key for access
    access_level: Enum  # read_only, comment, edit
    
    # Security and tracking
    created_at: datetime
    expires_at: Optional[datetime]  # Optional expiration
    is_active: bool
    
    # Usage stats
    view_count: int
    last_viewed_at: Optional[datetime]
    
    # Creator info
    created_by: Optional[str]  # User ID or API key
```

## Relationships

```
Document ───┬─── Section ───┬─── Note
            │               │
            │               ├─── Comment
            │               │
            │               ├─── Annotation
            │               │
            │               └─── Figure
            │
            ├─── Reference
            │
            └─── ShareLink
```

- **Document** is the central entity
- **Section** belongs to a Document and can have a parent-child relationship with other Sections
- **Note**, **Comment**, and **Annotation** belong to either a Document or a specific Section
- **Figure** belongs to a Document or a specific Section
- **Reference** belongs to a Document and can be linked to specific Sections
- **ShareLink** belongs to a Document

## Implementation Approach

The implementation of this data model will be done using SQLAlchemy ORM with Alembic for migrations. We will follow these steps:

1. **Phase 1**: Implement the core `Document` model
2. **Phase 2**: Add the `Section` model and establish the relationship with Document
3. **Phase 3**: Implement `Note`, `Comment`, and `Annotation` models
4. **Phase 4**: Add the `Reference` and `Figure` models
5. **Phase 5**: Implement the `ShareLink` model

## Database Considerations

1. **Indexing Strategy**:
   - Index on document title and metadata for search
   - Index on section titles and document_id for fast retrieval
   - Index on start_offset/end_offset for efficient annotation and comment retrieval

2. **Transactions**:
   - Use database transactions for operations that modify multiple tables
   - Ensure document updates and content parsing are handled atomically

3. **Performance**:
   - Consider partitioning for large document libraries
   - Use JSON field type for arrays and complex data
   - Implement proper cascading delete rules

4. **Future Extensions**:
   - Support for user accounts and multi-user collaboration
   - Full-text search capabilities
   - Version control for documents and annotations