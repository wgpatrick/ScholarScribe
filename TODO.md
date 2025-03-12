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
- [x] Implement SQLAlchemy models:
  - [x] Document model with metadata fields
  - [x] Section model for document structure
  - [x] Note, Comment, and Annotation models for user interactions
  - [x] Reference model for citations
  - [x] Figure model for tables and images
  - [x] ShareLink model for document sharing
- [x] Set up SQLAlchemy and Alembic for migrations
- [x] Create initial migration script
- [x] Run initial migration
- [x] Create base repository pattern for data access
- [x] Complete repositories for core PDF processing flow:
  - [x] Implement Document repository
  - [x] Implement Section repository with hierarchical query support
  - [x] Implement Reference repository
  - [x] Implement Figure repository
  - [x] Add transaction management for multi-entity operations
  - [ ] Create repository integration tests with actual database
- [ ] Implement repositories for user interaction models (Phase 3):
  - [ ] Implement Note repository
  - [ ] Implement Comment repository
  - [ ] Implement Annotation repository
  - [ ] Implement ShareLink repository

### File Upload & Storage (Backend)
- [x] Install dependencies (fastapi, python-multipart)
- [x] Create basic storage module for files
- [x] Create full storage abstraction layer:
  - [x] Implement consistent interface for both local files and S3
  - [x] Add file metadata extraction (size, hash, etc.)
  - [x] Create helper functions for generating storage paths
  - [x] Add error handling for storage failures
- [x] Create Pydantic schemas for API validation:
  - [x] DocumentCreate schema for upload validation
  - [x] DocumentResponse schema for API responses
  - [x] Section schemas for hierarchical structure
  - [x] Reference schemas for citation data
  - [x] Figure schemas for visual elements
- [x] Implement document upload workflow:
  - [x] Create upload endpoint with multipart form support
  - [x] Validate uploaded PDF (type, size, content)
  - [x] Store PDF using storage abstraction
  - [x] Create initial document record in database
  - [x] Return document ID and metadata

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
- [x] Create document processing service:
  - [x] Implement asynchronous processing task queue
  - [x] Create PDF conversion service integrated with database
  - [x] Implement document update workflow with status tracking
  - [x] Add detailed progress reporting
  - [x] Create error recovery mechanisms for failed conversions
- [x] Implement structured data extraction and storage:
  - [x] Create section extraction service that builds hierarchical structure
  - [x] Implement reference extraction and citation linking
  - [x] Add figure and table extraction with proper section linking
  - [x] Store all extracted entities in the database with proper relationships
- [x] Create document processing endpoints:
  - [x] Implement processing status endpoint
  - [x] Create endpoint for retrieving processed document with sections
  - [x] Add endpoint for document metadata with references
  - [x] Create endpoint for retrieving figures/tables
- [x] Implement comprehensive integration tests for the full workflow:
  - [x] Test upload → process → retrieve workflow
  - [x] Test error handling and recovery
  - [x] Measure conversion quality and performance metrics
  - [x] Create benchmarks for different paper types

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
- [ ] Repository and Database Testing:
  - [ ] Create database test fixtures with pytest-postgresql
  - [ ] Implement repository unit tests for all CRUD operations
  - [ ] Test complex queries (hierarchical sections, references)
  - [ ] Test transaction management and error handling
  - [ ] Verify cascade delete behavior
- [ ] API and Integration Testing:
  - [ ] Create test fixtures for file upload and storage testing
  - [ ] Implement end-to-end tests for document upload workflow
  - [ ] Test document processing pipeline with different paper types
  - [ ] Create test fixtures to mock LLM API calls
  - [ ] Test error scenarios and recovery mechanisms
- [ ] CI/CD and Quality Assurance:
  - [ ] Set up test coverage reporting with minimum 70% target
  - [ ] Create test automation for CI pipeline
  - [ ] Add performance benchmarks for processing time
  - [ ] Implement visual regression testing for frontend (Phase 4+)
  - [ ] Create integration tests for frontend-backend communication

## Phase 2: LLM Integration for Outline & Summaries

### Database Changes
- [x] Create sections table
- [x] Update migrations

### Heading Extraction
- [x] Implement markdown heading parser in structured data extractor
- [x] Build hierarchical section representation
- [x] Store sections in database

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
- [x] Create annotations table
- [x] Update migrations

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
- [x] Create references table
- [x] Update migrations

### Reference Parsing
- [x] Implement reference section detection
- [x] Extract individual references
- [x] Parse DOIs or identifiers
- [x] Store in database

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
- [x] Create share_links table (no need for users table in MVP)
- [x] Update migrations

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