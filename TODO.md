# Journal Notebook - Detailed To-Do List

This document tracks all development tasks for the Journal Notebook project. As we complete tasks, we'll mark them as done.

## Phase 1: PDF Upload & Markdown Conversion

### Project Setup
- [ ] Initialize Git repository
- [ ] Add .gitignore for Python and Node
- [ ] Initialize backend (FastAPI)
- [ ] Set up Docker and docker-compose for local development
- [ ] Create health-check endpoint
- [ ] Initialize frontend (React with Vite)
- [ ] Set up environment/config files (.env for secrets)

### Local Development Environment
- [ ] Set up Docker container for PostgreSQL
- [ ] Create development environment documentation
- [ ] Configure local file storage for PDFs
- [ ] Set up mock S3 service (or LocalStack) for testing
- [ ] Implement centralized error logging system
- [ ] Create error monitoring dashboard
- [ ] Set up structured error response format
- [ ] Configure detailed logging for critical components

### Database Configuration
- [ ] Set up PostgreSQL with Docker
- [ ] Design SQLAlchemy models:
  - [ ] Document model with metadata fields
  - [ ] Define proper column types and relationships
  - [ ] Add validation rules and constraints
- [ ] Set up SQLAlchemy and Alembic for migrations
- [ ] Create initial migration script
- [ ] Run initial migration
- [ ] Create repository pattern for data access
- [ ] Set up transaction management

### File Upload (Backend)
- [ ] Install dependencies (fastapi, python-multipart)
- [ ] Create storage abstraction layer (works with local files now, S3 later)
- [ ] Implement upload route
- [ ] Store document record in database

### PDF to Structured Markdown Conversion (Critical Path)
- [ ] Set up PyMuPDF4LLM library
- [ ] Create comprehensive PDF to Structured Markdown conversion utility
- [ ] Implement robust parsing of academic paper structure:
  - [ ] Accurate heading detection with hierarchy preservation
  - [ ] Paragraph and text block identification
  - [ ] Table and figure detection
  - [ ] Reference section identification
  - [ ] Citation linking
- [ ] Build extensive test suite with diverse academic paper samples
- [ ] Create conversion endpoint with detailed progress tracking
- [ ] Update database with structured markdown text
- [ ] Implement detailed error handling and fallback options
- [ ] Add conversion quality metrics
- [ ] Develop iterative improvement process based on test results
- [ ] Create documentation for the conversion pipeline

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
- [ ] Set up pytest for backend testing with coverage reporting
- [ ] Create test fixtures for database and file operations
- [ ] Create mock dataset of diverse academic papers for testing
- [ ] Implement snapshot testing for PDF conversion outputs
- [ ] Write comprehensive tests for PDF conversion pipeline (90%+ coverage target)
- [ ] Write integration tests for storage abstraction layer
- [ ] Implement end-to-end tests for critical user flows
- [ ] Set up test fixtures to mock OpenAI API calls
- [ ] Create test automation for CI pipeline
- [ ] Implement visual regression testing for frontend

## Phase 2: LLM Integration for Outline & Summaries

### Database Changes
- [ ] Create sections table
- [ ] Update migrations

### Heading Extraction
- [ ] Implement markdown heading parser
- [ ] Store sections in database

### OpenAI GPT-4o Integration
- [ ] Set up OpenAI API client with API key management
- [ ] Create summary generation function using GPT-4o
- [ ] Develop optimized prompts for academic content summarization
- [ ] Implement cost tracking and usage monitoring
- [ ] Add caching layer to prevent duplicate LLM calls
- [ ] Implement fallback handling for API rate limits
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