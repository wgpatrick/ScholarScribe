#!/usr/bin/env python
import os
import sys
import subprocess
from dotenv import load_dotenv

def run_migration():
    """
    Run database migrations using Alembic
    """
    print("Running database migrations...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if we have a database connection
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.")
        sys.exit(1)
        
    print(f"Using DATABASE_URL: {database_url}")
    
    # Run Alembic upgrade to our new_data_model revision directly
    try:
        # First try to check the current state
        subprocess.run(
            ["alembic", "current"], 
            check=True,
            env={**os.environ, "PYTHONPATH": "."}
        )
        
        # Run the upgrade to our new migration
        subprocess.run(
            ["alembic", "upgrade", "new_data_model"], 
            check=True,
            env={**os.environ, "PYTHONPATH": "."}
        )
        print("Migration completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Migration failed with exit code {e.returncode}")
        print("Try running: alembic upgrade new_data_model")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()