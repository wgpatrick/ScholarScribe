#\!/bin/bash
# Setup script for Journal Notebook

# Create Python virtual environment
cd backend
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Start PostgreSQL with Docker
cd ..
docker-compose up -d

# Wait for PostgreSQL to start
echo "Waiting for PostgreSQL to start..."
sleep 5

# Run database migrations
cd backend
. venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

echo "Setup complete\! PostgreSQL is running with initial schema."
echo "You can start the API with:"
echo "cd backend && . venv/bin/activate && uvicorn app.main:app --reload"
