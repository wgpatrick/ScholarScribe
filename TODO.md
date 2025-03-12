# ScholarScribe - Detailed To-Do List

This document tracks all development tasks for the ScholarScribe project. As we complete tasks, we'll mark them as done.

## Phase 1: PDF Upload & Markdown Conversion

### Project Setup
- [x] Initialize Git repository
- [x] Add .gitignore for Python and Node
- [x] Initialize backend (FastAPI)
- [x] Set up Docker and docker-compose for local development
- [x] Create health-check endpoint
- [x] Initialize frontend (placeholder)
- [x] Set up environment/config files (.env for secrets)

### Local Development Environment
- [x] Configure local file storage for PDFs
- [x] Configure detailed logging for critical components
- [x] Implement structured error handling and reporting
- [x] Set up Docker container for PostgreSQL
- [x] Create development environment documentation
- [x] Set up mock S3 service (LocalStack) for testing
- [x] Implement centralized error logging system
- [x] Create error monitoring dashboard

### Database Configuration
- [x] Set up PostgreSQL with Docker
- [x] Design comprehensive data model (see docs/DATA_MODEL.md)
- [ ] Implement SQLAlchemy models:
  - [ ] Document model with metadata fields
  - [ ] Section model for document structure
  - [ ] Note, Comment, and Annotation models for user interactions
  - [ ] Reference model for citations
  - [ ] Figure model for tables and images
  - [ ] ShareLink model for document sharing
- [ ] Set up SQLAlchemy and Alembic for migrations
- [ ] Create initial migration script
- [ ] Run initial migration
- [ ] Create repository pattern for data access
- [ ] Set up transaction management

### File Upload (Backend)
- [x] Install dependencies (fastapi, python-multipart)
- [x] Create basic storage module for files
- [ ] Create full storage abstraction layer (works with local files now, S3 later)
- [ ] Implement upload route with validation
- [ ] Store document record in database

### PDF to Structured Markdown Conversion (Critical Path)
- [x] Evaluate and implement PDF parsing libraries:
  - [x] PyMuPDF4LLM for local fallback
  - [x] LlamaParse integration for cloud-based parsing
- [x] Create comprehensive PDF to Structured Markdown conversion utility
- [x] Implement robust parsing of academic paper structure:
  - [x] Accurate heading detection with hierarchy preservation
  - [x] Paragraph and text block identification
  - [x] Table and figure detection
  - [x] Reference section identification
  - [x] Basic citation linking
- [x] Build test suite with diverse academic paper samples
- [x] Implement structured data extraction from parsed content
- [x] Create fallback mechanisms for offline/failed parsing
- [x] Implement detailed error handling and logging
- [x] Design multi-layer fallback strategy for robustness
- [x] Create documentation for the parsing pipeline
- [ ] Create conversion endpoint with detailed progress tracking
- [ ] Update database with structured markdown text
- [ ] Add conversion quality metrics
- [ ] Develop iterative improvement process based on test results

### Frontend Integration
- [ ] Set up React project with TypeScript
- [ ] Create Context API providers for state management:
  - [ ] DocumentContext for current document state
  - [ ] UIContext for UI state (loading, errors, etc.)
- [ ] Implement custom hooks for document operations
- [ ] Create upload form component
- [ ] Implement API client for backend communication
- [ ] Create document view page with toggle between PDF and Markdown
- [ ] Implement markdown rendering with syntax highlighting
- [ ] Add loading states and progress indicators
- [ ] Implement error boundary components
- [ ] Create reusable UI components library

### Testing Strategy Implementation
- [x] Set up pytest for backend testing
- [x] Create mock dataset of diverse academic papers for testing
- [x] Implement comparison testing for PDF conversion outputs
- [x] Create diagnostic tools for parser validation
- [x] Implement various test scripts for different parsing methods
- [x] Develop metrics collection for parser quality assessment
- [ ] Set up test coverage reporting
- [ ] Create test fixtures for database and file operations
- [ ] Write integration tests for storage abstraction layer
- [ ] Implement end-to-end tests for critical user flows
- [ ] Set up test fixtures to mock LLM API calls
- [ ] Create test automation for CI pipeline
- [ ] Implement visual regression testing for frontend

## Phase 2: LLM Integration for Outline & Summaries

### Database Changes
- [ ] Create sections table
- [ ] Update migrations

### Heading Extraction
- [x] Implement markdown heading parser in structured data extractor
- [x] Build hierarchical section representation
- [ ] Store sections in database

### LLM Integration
- [x] Set up LlamaCloud API client with API key management
- [x] Implement LlamaParse for document parsing and structure extraction
- [x] Develop optimized prompts for academic document parsing
- [x] Implement fallback handling for API rate limits and connectivity issues
- [ ] Create summary generation function using LLMs
- [ ] Implement cost tracking and usage monitoring
- [ ] Add caching layer to prevent duplicate LLM calls
- [ ] Create document summarization endpoint with progress tracking

### Frontend Components
- [ ] Create outline component
- [ ] Fetch and display document sections
- [ ] Render summaries under headings
- [ ] Implement navigation between outline and content

### Testing
- [ ] Test heading extraction with various documents
- [ ] Test summary generation
- [ ] Verify UI displays correctly

## Phase 3: Annotation System

### Database Changes
- [ ] Create annotations table
- [ ] Update migrations

### Automatic Term Detection
- [ ] Implement term detection logic
- [ ] Create OpenAI prompt for term identification
- [ ] Generate definitions for detected terms
- [ ] Store annotations in database

### User-Requested Definitions
- [ ] Create annotation endpoint for user highlights
- [ ] Implement OpenAI call for definitions
- [ ] Store user-requested annotations

### Frontend Integration
- [ ] Render annotated terms with highlighting
- [ ] Implement tooltip/popup for definitions
- [ ] Create text selection UI for requesting definitions
- [ ] Handle UI updates after new annotations

### Testing
- [ ] Test automatic term detection
- [ ] Test user-requested definitions
- [ ] Verify UI behavior with annotations

## Phase 4: Reference Extraction & Metadata

### Database Changes
- [ ] Create references table
- [ ] Update migrations

### Reference Parsing
- [ ] Implement reference section detection
- [ ] Extract individual references
- [ ] Parse DOIs or identifiers
- [ ] Store in database

### External API Integration
- [ ] Implement CrossRef/PubMed API client
- [ ] Create metadata fetching function
- [ ] Update references with fetched data
- [ ] Create references endpoint

### Frontend Components
- [ ] Create references list component
- [ ] Implement reference detail view
- [ ] Link in-text citations to references
- [ ] Display metadata in side panel

### Testing
- [ ] Test reference parsing with sample papers
- [ ] Test API integration with real DOIs
- [ ] Verify UI display of references

## Phase 5: Sharing & Access Control

### Database Changes
- [ ] Create share_links table (no need for users table in MVP)
- [ ] Update migrations

### Sharing Backend
- [ ] Implement API key validation for admin access
- [ ] Create share link generation endpoint
- [ ] Implement read-only document access

### Frontend Integration
- [ ] Add share button for document owners
- [ ] Create shareable link display
- [ ] Implement read-only view for shared documents
- [ ] Hide editing features in shared view

### Testing
- [ ] Test share link generation
- [ ] Test read-only access restrictions
- [ ] Verify end-to-end sharing flow

## AWS Deployment (Post-MVP)

### AWS Infrastructure
- [ ] Set up AWS account and IAM roles
- [ ] Create S3 buckets for PDFs and frontend hosting
- [ ] Set up RDS PostgreSQL instance
- [ ] Configure Lambda for backend API

### Deployment Pipeline
- [ ] Create CI/CD pipeline with GitHub Actions
- [ ] Set up automated testing in pipeline
- [ ] Create deployment scripts for frontend and backend
- [ ] Configure CloudFront for frontend delivery

### Environment Configuration
- [ ] Set up environment variables in AWS
- [ ] Configure secrets management
- [ ] Update storage layer to use S3
- [ ] Test entire flow in cloud environment