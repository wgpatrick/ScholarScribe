# ScholarScribe Development Guide

This guide provides instructions for setting up and working with the ScholarScribe development environment.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.9+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/) (for frontend development)
- Git

## Project Structure

```
ScholarScribe/
├── backend/               # FastAPI backend application
│   ├── app/               # Application code
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core configuration
│   │   ├── db/            # Database models and setup
│   │   ├── models/        # Pydantic models
│   │   ├── services/      # Business logic services
│   │   │   └── pdf_parsing/  # PDF processing services
│   │   └── utils/         # Utility functions
│   ├── migrations/        # Alembic database migrations
│   ├── storage/           # Local file storage
│   └── tests/             # Test files
├── docs/                  # Project documentation
│   └── DATA_MODEL.md      # Database schema and relations documentation
├── frontend/              # React frontend (to be implemented)
├── docker-compose.yml     # Docker services configuration
├── setup.sh               # Setup script
└── .env                   # Environment variables (not in git)
```

## Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/wgpatrick/ScholarScribe.git
   cd ScholarScribe
   ```

2. **Create your .env file**:
   ```bash
   cp backend/.env.template backend/.env
   # Edit backend/.env with your API keys and configuration
   ```

3. **Start the Docker services**:
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database on port 5432
   - pgAdmin (PostgreSQL management) on port 5050
   - LocalStack (mock AWS services) on port 4566

4. **Set up the backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Run database migrations**:
   ```bash
   # With the virtual environment activated
   alembic upgrade head
   ```

6. **Set up LocalStack S3 bucket**:
   ```bash
   # Install AWS CLI
   pip install awscli

   # Configure AWS CLI for LocalStack
   aws configure set aws_access_key_id test
   aws configure set aws_secret_access_key test
   aws configure set region us-east-1

   # Create S3 bucket
   aws --endpoint-url=http://localhost:4566 s3 mb s3://scholarscribe-documents
   ```

## Running the Application

### Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m app.main
```

The FastAPI server will run at http://localhost:8000

- API documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Database Management

Access pgAdmin at http://localhost:5050
- Email: admin@scholarscribe.com
- Password: admin

To connect to the PostgreSQL database:
1. Add New Server
2. Name: ScholarScribe
3. Connection tab:
   - Host: db
   - Port: 5432
   - Username: scholarscribe_user
   - Password: scholarscribe_password
   - Database: scholarscribe_db

### Database Structure and Data Model

The ScholarScribe database model is fully implemented with SQLAlchemy and includes:

- **Document**: Central entity with metadata and content
- **Section**: Hierarchical document structure with parent-child relationships
- **Reference**: Citations and bibliography entries
- **Figure**: Tables, images, and other visual elements
- **Note**, **Comment**, **Annotation**: Different types of user content
- **ShareLink**: Document sharing functionality

All models use UUID primary keys for better distributed systems compatibility.

The Repository Pattern is implemented to abstract database access:

- **BaseRepository**: Generic CRUD operations for all models
- **DocumentRepository**: Document-specific operations and queries
- **SectionRepository**: Specialized for hierarchical section structure
- **ReferenceRepository**: Bibliography and citation handling
- **FigureRepository**: Figure and table management

Transactions are managed through context managers to ensure atomic operations.

The data model is documented in detail in [docs/DATA_MODEL.md](docs/DATA_MODEL.md), including:

- Entity relationships and cardinality
- Field definitions and data types
- Implementation approach using SQLAlchemy

When designing new features, consult this document to understand how data should be structured and stored.

### S3 Storage

LocalStack provides an S3-compatible API at http://localhost:4566

Use the AWS CLI with the `--endpoint-url` parameter:
```bash
# List buckets
aws --endpoint-url=http://localhost:4566 s3 ls

# List objects in scholarscribe-documents bucket
aws --endpoint-url=http://localhost:4566 s3 ls s3://scholarscribe-documents
```

## Error Logging

Logs are written to both the console and `backend/app.log`. The log level can be configured via the `LOG_LEVEL` environment variable.

## Testing

The project includes comprehensive tests for the repository layer and API endpoints.

### Repository Tests

Tests for database repositories are located in `backend/tests/db/`:
```bash
cd backend
# Install test dependencies
pip install -r tests/requirements.txt

# Run repository tests that interact with a real PostgreSQL database
PYTHONPATH=$PYTHONPATH:/path/to/ScholarScribe/backend pytest -xvs tests/db/
```

These tests verify CRUD operations, hierarchical data handling, and relationships between entities.

### API Tests

Tests for API endpoints:
```bash
cd backend
pytest tests/api/
```

### Full Flow Tests

To test the complete document upload → processing → retrieval flow:
```bash
cd backend
python test_full_flow.py tests/pdf_corpus/papers/cs/attention_is_all_you_need.pdf
```

This runs the full pipeline from PDF upload through LlamaParse processing to database storage.

For more verbose output on any test:
```bash
pytest -v
```

## Common Development Tasks

### Adding a New Dependency

```bash
cd backend
pip install new-package
pip freeze > requirements.txt
```

### Creating a Database Migration

After modifying database models:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Modifying the Data Model

When you need to make changes to the data model:

1. Update the SQLAlchemy models in `backend/app/db/models/`
2. Update the [Data Model documentation](docs/DATA_MODEL.md) to reflect your changes
3. Create and run an Alembic migration
4. Update any affected API endpoints or services

### Accessing LLM Services

The application uses LlamaCloud API for document parsing and OpenAI for additional processing. Make sure to set the appropriate API keys in your `.env` file.

## Troubleshooting

### Database Connection Issues

- Ensure the PostgreSQL container is running:
  ```bash
  docker ps | grep postgres
  ```
- Check the database logs:
  ```bash
  docker-compose logs db
  ```

### LocalStack Issues

- Ensure the LocalStack container is running:
  ```bash
  docker ps | grep localstack
  ```
- Check the LocalStack logs:
  ```bash
  docker-compose logs localstack
  ```

### PDF Processing Issues

- For PDF parsing errors, check the detailed logs in `backend/app.log`
- Ensure your LlamaCloud API key is correct in the `.env` file
- The system has fallbacks to PyMuPDF for situations where LlamaParse is unavailable

## Useful Commands

```bash
# Restart all containers
docker-compose restart

# Stop all containers
docker-compose down

# View container logs
docker-compose logs -f

# Run a single backend test file
cd backend
pytest tests/path/to/test_file.py -v

# Generate a coverage report
cd backend
pytest --cov=app tests/
```