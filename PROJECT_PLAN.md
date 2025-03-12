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

### Phase 1: PDF Upload & Structured Markdown Conversion
- Upload and store PDFs
- Develop robust PDF-to-Structured-Markdown pipeline using LlamaParse
- Implement multi-layer fallback strategy with PyMuPDF for offline operation
- Extract structured data from academic papers (headings, paragraphs, references, etc.)
- Implement extensive testing with various academic paper formats
- Refine the conversion pipeline until high quality is achieved
- Display both formats with toggle between them

> **Note**: The PDF-to-Markdown conversion pipeline is the most critical component of the application. We've implemented LlamaParse as the primary method with local fallbacks to ensure robust operation in all scenarios.

### Phase 2: Enhanced LLM Integration for Summaries
- Build on the existing LlamaCloud integration 
- Generate focused summaries for each section via appropriate LLMs
- Extract key concepts from academic content
- Display structured outline with summaries

### Phase 3: Annotation System
- Auto-detect domain-specific terms
- Generate definitions using appropriate LLMs
- Allow users to highlight text for custom definitions
- Implement UI for viewing annotations
- Create interactive popup system for annotations

### Phase 4: Reference Extraction & Metadata
- Parse references from the document
- Fetch metadata from external APIs (CrossRef, PubMed, etc.)
- Display reference data in side panel when clicked

### Phase 5: Sharing & Access Control
- Generate shareable read-only links
- Restrict editing capabilities for shared viewers
- Hide PDF view for non-owners

## Key Data Models

1. **Documents**
   - Basic metadata (title, authors if parsed)
   - PDF storage path
   - Markdown content

2. **Sections**
   - Heading text and level
   - Section content
   - Generated summary

3. **Annotations**
   - Term or text snippet
   - Definition (auto or user-requested)
   - Position markers

4. **References**
   - Raw citation text
   - Extracted DOI (if available)
   - Fetched metadata (title, abstract, citation count)

5. **Share Links**
   - Document ID
   - Unique share key

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

## Timeline

The project will proceed through the 5 phases sequentially, with each phase building on the previous one. We'll track progress in our detailed to-do list.