# ScholarScribe - Project Plan

## Project Overview

ScholarScribe is a web-based reader/notebook application for academic journal articles. It allows users to upload PDFs and instantly view both the original PDF and a structured Markdown version with the following features:

- Auto-generated outlines and short summaries
- Key term annotations with definitions
- Reference previews and summaries
- Inline user notes
- Easy sharing of read-only Markdown documents

The goal is to help researchers and students learn more quickly, especially when exploring academic papers outside their primary domain.

## Technical Architecture

1. **Backend**: Python with FastAPI, hosted on AWS Lambda (local development first)
2. **Frontend**: React with Context API for state management
3. **Database**: PostgreSQL with SQLAlchemy ORM (local for development, AWS RDS for production)
4. **File Storage**: AWS S3 for PDFs (local file system during development)
5. **PDF Processing**: LlamaParse with fallback to PyMuPDF for robust academic paper parsing
6. **LLM Integration**: LlamaCloud API for document parsing and OpenAI for summaries and annotations
7. **Authentication**: Simple API key for initial MVP (no user accounts)
8. **Testing**: Pytest with focus on integration tests (70% coverage target, 90%+ for PDF conversion)
9. **Error Handling**: Graceful degradation with detailed logging and monitoring

### Development Approach

We've decided on a two-phase development approach:

1. **Local Development Phase**:
   - Develop the entire application locally
   - Use Docker for PostgreSQL database
   - Store files in local filesystem
   - Mock S3 interactions when needed (or use LocalStack)
   - Fast iteration cycle without deployment delays

2. **Cloud Deployment Phase**:
   - Deploy to AWS when ready for staging/production
   - Use Lambda for backend API
   - Use S3 for file storage
   - Use RDS for PostgreSQL database
   - Set up CloudFront for frontend delivery

## Development Phases

### Phase 1: PDF Upload & Structured Markdown Conversion ✅
- ✅ Upload and store PDFs with local and S3 storage services
- ✅ Develop robust PDF-to-Structured-Markdown pipeline using LlamaParse
- ✅ Implement multi-layer fallback strategy with PyMuPDF for offline operation
- ✅ Extract structured data from academic papers (headings, paragraphs, references, figures)
- ✅ Design and implement database models with comprehensive repository layer
- ✅ Create test suite for validating repository functionality
- ✅ Implement document processor for coordinating the complete pipeline
- ✅ Create basic API endpoints for document operations
- ✅ Validate complete flow from upload to structured data storage

> **Status**: The PDF processing and backend functionality for Phase 1 are complete. We have implemented a robust pipeline with LlamaParse and fallback mechanisms. The database schema is implemented with repository patterns and comprehensive tests.

### Phase 1.5: Frontend Development 🔄 (Current Focus)
- 🔄 Set up React project with TypeScript
- 🔄 Create document upload component
- 🔄 Implement document list view
- 🔄 Build document viewer with toggle between PDF and Markdown
- 🔄 Add navigation for document sections
- 🔄 Implement API client for backend communication
- 🔄 Add user interface for viewing document structure
- 🔄 Create visualization for references and figures

### Phase 2: Enhanced LLM Integration for Summaries
- ✅ Integrate with LlamaCloud API
- 🔄 Generate focused summaries for each section via appropriate LLMs
- 🔄 Extract key concepts from academic content
- 🔄 Display structured outline with summaries

### Phase 3: Annotation System
- ✅ Design database models for annotations
- 🔄 Implement repository layer for annotation operations
- 🔄 Auto-detect domain-specific terms
- 🔄 Generate definitions using appropriate LLMs
- 🔄 Allow users to highlight text for custom definitions
- 🔄 Implement UI for viewing annotations
- 🔄 Create interactive popup system for annotations

### Phase 4: Reference Extraction & Metadata
- ✅ Design and implement reference models
- ✅ Parse references from the document
- 🔄 Fetch metadata from external APIs (CrossRef, PubMed, etc.)
- 🔄 Display reference data in side panel when clicked

### Phase 5: Sharing & Access Control
- ✅ Design database models for sharing functionality
- 🔄 Implement repository layer for share links
- 🔄 Generate shareable read-only links
- 🔄 Restrict editing capabilities for shared viewers
- 🔄 Hide PDF view for non-owners

## Key Data Models ✅

All data models have been implemented with SQLAlchemy ORM and use UUID primary keys.

1. **Documents** ✅
   - Basic metadata (title, authors, abstract)
   - PDF metadata (path, hash, size)
   - Processing information (status, method, time)
   - Markdown content
   - View tracking (count, last viewed)

2. **Sections** ✅
   - Hierarchical structure with parent-child relationships
   - Heading text and level
   - Section content
   - Order within parent section
   - Metadata (word count, has_figures, has_tables, has_equations)
   - Keywords

3. **Annotations** ✅
   - Term or text snippet
   - Definition (auto or user-requested)
   - Position markers
   - User-specific flags

4. **References** ✅
   - Raw citation text
   - Structured metadata (title, authors, year, venue)
   - Extracted DOI and URL
   - Order within document

5. **Figures** ✅
   - Figure type (figure, table, equation)
   - Caption
   - Reference ID (e.g., "Figure 1")
   - Image path or content (for tables)
   - Section relationship

6. **Share Links** ✅
   - Document ID
   - Unique share key
   - Access expiration
   - View tracking

## Tech Stack

- **Frontend**: React
- **Backend**: Python + FastAPI
- **Database**: PostgreSQL
- **Storage**: AWS S3
- **AI**: LlamaCloud API + OpenAI API
- **PDF Processing**: LlamaParse with PyMuPDF fallback
- **Deployment**: AWS (Lambda, S3, CloudFront)

## Post-MVP Features

Features to consider after completing the MVP:

1. **Enhanced Collaboration**:
   - Real-time collaborative annotation
   - Comments on shared documents
   - Multiple owner permissions

2. **Advanced PDF Processing**:
   - Better handling of tables and figures
   - Math equation rendering and annotation
   - OCR for scanned papers
   - Self-hosted LLM options for complete offline operation

3. **Integration with Research Tools**:
   - Citation management integration (Zotero, Mendeley)
   - Export to reference managers
   - Integration with academic search engines
   - Literature recommendation based on paper content

4. **Advanced UI Features**:
   - Dark mode
   - Customizable interface
   - Mobile app version
   - Voice annotations and queries

5. **Enterprise Features**:
   - Team/organization accounts
   - SSO integration
   - Compliance features for institutional use
   - Private LLM integration for sensitive documents

## Timeline and Progress

### Current Status
- ✅ **Phase 1 (Backend)**: Complete - All backend functionality for PDF processing and database operations is implemented
- 🔄 **Phase 1.5 (Frontend)**: In Progress - Building React frontend for document viewing and interaction
- 🔄 **Phase 2-5**: Partially implemented in database schema, awaiting frontend and advanced features

### Next Milestones
1. Complete the frontend MVP for document viewing 
2. Implement section navigation and reference display
3. Add user authentication and document ownership
4. Develop advanced LLM features for summaries and annotations

We track detailed progress in [TODO.md](TODO.md)