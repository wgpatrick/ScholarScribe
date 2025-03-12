# ScholarScribe

ScholarScribe is an academic paper reader and note-taking application designed to enhance the research experience. It converts academic PDFs into structured formats for better reading, annotation, and analysis.

## Features

- PDF parsing with [LlamaCloud API](https://docs.llamaindex.ai/en/latest/api_reference/llama_parse/)
- Structured data extraction from academic papers
- Hierarchical document navigation
- Robust fallback mechanisms for offline usage
- Markdown output format

## Project Structure

- **`/backend`**: Python FastAPI backend with PDF processing capabilities
  - LlamaParse integration for academic paper parsing
  - Structured data extraction
  - API endpoints for document management
  
- **`/frontend`**: React frontend for the web application (in development)
  - User interface for reading and annotating papers
  - Document navigation

## Getting Started

1. Clone the repository
2. Set up environment variables (see `.env.template` in backend directory)
3. Run the setup script: `./setup.sh`
4. Start the backend server: `cd backend && python -m app.main`
5. Frontend setup (coming soon)

## Development Status

This project is in active development:

### Completed
- Database implementation with SQLAlchemy
- Repository pattern for data access with comprehensive tests
- PDF parsing with LlamaParse integration
- Structured data extraction
- Storage service with local and S3 support
- Document processing pipeline
- Hierarchical section structure
- Reference and figure extraction

### Current Focus
- Frontend development with React and TypeScript
- User interface for document view and annotation
- Enhanced PDF processing capabilities
- API endpoint testing

### Coming Soon
- User authentication and access control
- Sharing functionality
- Advanced LLM features (summarization, term definitions)
- Citation management

See [TODO.md](TODO.md) for detailed progress tracking and upcoming tasks.

## License

MIT
