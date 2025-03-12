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

Run tests with pytest:
```bash
cd backend
pytest
```

For more verbose output:
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