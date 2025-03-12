# ScholarScribe Frontend - Development Guide

This document provides instructions for running and developing the ScholarScribe frontend.

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend server running (see main project README)

### Installation

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Access the application at http://localhost:5173

## Development Features

The frontend currently includes:

1. **Library Dashboard**
   - Document grid/list view with search functionality
   - Upload new document functionality
   - Processing status indicators

2. **Document Viewer**
   - Basic document display with Markdown rendering
   - Toggle between Markdown and PDF views (PDF view in development)
   - Section navigation sidebar
   - Placeholder for annotations and references

3. **Upload System**
   - Drag-and-drop file upload
   - Processing status tracking
   - Error handling

## API Integration

The frontend is designed to work with the ScholarScribe backend API. Currently, it uses mock data, but API integration functions have been created in:

- `src/api/client.ts` - Base API client
- `src/api/documents.ts` - Document-specific API endpoints

To switch from mock data to real API calls, uncomment the API calls in the components.

## Next Steps

1. Implement PDF viewer with React-PDF
2. Add position synchronization between PDF and Markdown views
3. Develop section summary display in the navigation sidebar
4. Create components for annotations and references

## Troubleshooting

- If you encounter CORS issues, ensure the Vite proxy settings in `vite.config.ts` are correctly configured
- For TypeScript errors, run `npm run type-check` to identify issues
- If components don't render as expected, check browser developer console for errors