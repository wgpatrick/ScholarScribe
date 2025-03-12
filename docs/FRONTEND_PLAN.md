# ScholarScribe Frontend Implementation Plan

This document outlines the detailed implementation plan for the ScholarScribe frontend, including the necessary backend API extensions to support the planned features.

## Overview

ScholarScribe's frontend will provide researchers with an intuitive interface for uploading, reading, and annotating academic papers. The application will feature a modern, minimal design inspired by Notion, with a focus on typography and readability.

## Technology Stack

- **Framework**: React 18+ with TypeScript
- **Styling**: TailwindCSS for utility-first styling
- **State Management**: React Context API
- **UI Components**: Headless UI (for accessible components that pair with Tailwind)
- **PDF Viewer**: React-PDF for rendering PDFs
- **Markdown Rendering**: react-markdown with remark/rehype plugins
- **Build Tool**: Vite for fast development experience

## User Experience Design

### Core Layout

```
+-------------------------------------------+
| Navbar                                    |
+--------+------------------+---------------+
|        |                  |               |
|        |                  |               |
| Outline|  Document View   |  Side Panel   |
| Nav    |  (Markdown/PDF)  |  (Annotations,|
|        |                  |   References) |
|        |                  |               |
|        |                  |               |
+--------+------------------+---------------+
```

### Key User Flows

1. **Document Library and Upload**
   - User lands on library dashboard with recently viewed documents
   - User uploads new document via drag-and-drop or file browser
   - System processes document with progress indicators
   - Document appears in library when processing completes

2. **Document Reading**
   - User selects document from library
   - Document opens in Markdown view with section outline in left sidebar
   - User can toggle to PDF view with synchronized position
   - User navigates via outline with section summaries

3. **Annotation and References**
   - User hovers over annotated text to see highlight
   - User clicks on annotation to view details in right sidebar
   - User selects text to add comments (displayed with yellow background)
   - User clicks on references to view citation details in sidebar

## Implementation Progress

### Phase 1: Library Dashboard and Document Viewing ✅ (Initial Implementation)

**Completed Components:**
- ✅ Application layout and routing
- ✅ Library dashboard with document grid/list view toggle
- ✅ Document upload with drag-and-drop and progress tracking
- ✅ Document viewing with basic Markdown rendering
- ✅ PDF/Markdown toggle UI (PDF viewer placeholder in place)
- ✅ Document header with metadata display

**Remaining Tasks:**
- Context API implementation for state management
- Full PDF viewer implementation
- Enhanced error handling with boundary components

**Backend API Requirements:**
- Document upload endpoint (existing)
- Document listing endpoint (existing, needs enhancement)
- Document retrieval endpoint (existing)
- Processing status endpoint (existing)

### Phase 2: Document Navigation and Reading Experience

**Frontend Components:**
- Outline navigation in left sidebar with section summaries
- Section jumping functionality
- Document header with metadata
- Position synchronization between PDF and Markdown views

**Backend API Requirements:**
- Section structure endpoint (existing)
- Document with sections endpoint (existing)
- New dedicated TOC/outline endpoint (needed)
- Position mapping API (needed)

### Phase 3: Reference Display and Management

**Frontend Components:**
- Reference linking in document text
- Reference display in right sidebar
- Citation context display
- Document search functionality

**Backend API Requirements:**
- References retrieval endpoint (existing)
- Citation linking endpoint (needed)
- Document search endpoint (needed)
- Reference metadata enhancement (needed)

### Phase 4: Annotation and Comment System

**Frontend Components:**
- Text selection for annotations
- Annotation display inline and in sidebar
- User comment creation and editing
- Comment styling with distinct visual appearance

**Backend API Requirements:**
- Annotation CRUD endpoints (needed)
- Comment CRUD endpoints (needed)
- Position anchoring system (needed)
- Filtering and pagination for annotations (needed)

## Backend API Extensions Required

The following API extensions are needed to fully support the frontend implementation:

### 1. Document Management Enhancements

```
GET /documents?search={term}&sort={field}&order={asc|desc}&status={status}
```
Enhanced document listing with search, sorting, and filtering

```
GET /documents/recent
```
Recently viewed documents for dashboard

```
GET /documents/{document_id}/outline
```
Dedicated endpoint for document outline/TOC

### 2. Reading Experience Improvements

```
GET /documents/{document_id}/position?pdf_page={page}&pdf_y={y_coord}
```
Get corresponding Markdown position from PDF position

```
GET /documents/{document_id}/position?markdown_offset={offset}
```
Get corresponding PDF position from Markdown position

```
GET /documents/{document_id}/search?q={query}
```
Search within document content

### 3. Annotation and Comment System

```
GET /documents/{document_id}/annotations
POST /documents/{document_id}/annotations
GET /documents/{document_id}/annotations/{annotation_id}
PUT /documents/{document_id}/annotations/{annotation_id}
DELETE /documents/{document_id}/annotations/{annotation_id}
```
Annotation CRUD endpoints

```
GET /documents/{document_id}/comments
POST /documents/{document_id}/comments
GET /documents/{document_id}/comments/{comment_id}
PUT /documents/{document_id}/comments/{comment_id}
DELETE /documents/{document_id}/comments/{comment_id}
```
Comment CRUD endpoints

## Implementation Timeline

1. **Phase 1 (Library Dashboard and Document Viewing)**: 2-3 weeks
2. **Backend API Extensions for Phase 2**: 1-2 weeks
3. **Phase 2 (Document Navigation)**: 2-3 weeks
4. **Backend API Extensions for Phase 3**: 1-2 weeks
5. **Phase 3 (Reference Display)**: 2-3 weeks
6. **Backend API Extensions for Phase 4**: 2-3 weeks
7. **Phase 4 (Annotation System)**: 3-4 weeks

Total estimated timeline: 13-20 weeks

## Technical Challenges

### Position Synchronization
Synchronizing positions between PDF and Markdown views will be one of the most challenging aspects. We'll approach this by:
1. Using section headers as anchor points
2. Implementing content fingerprinting for position matching
3. Creating a mapping system between formats
4. Providing user controls for manual synchronization when needed

### Performance Optimization
For large academic papers:
1. Implement virtualized lists for long documents
2. Use lazy loading for PDF content
3. Implement chunked rendering for Markdown
4. Add efficient caching mechanisms for document content

## Design Principles

1. **Minimal, Clean Interface**
   - White background with subtle borders
   - Typography-focused design similar to Notion
   - Limited color palette with accent colors for interaction
   - Generous whitespace for readability

2. **Content Differentiation**
   - Original document content (default styling)
   - User-generated comments (light yellow background)
   - System-generated annotations (underlined with hover effect)
   - References and citations (subtle highlighting)

3. **Progressive Disclosure**
   - Start with simple document viewing
   - Reveal advanced features as needed
   - Collapsible UI elements for focused reading