#!/usr/bin/env python
"""
Create Tables Script

This script will create all database tables directly using SQLAlchemy models.
It bypasses Alembic migrations.
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models
from app.db.database import Base
from app.models.document import Document
from app.models.section import Section
from app.models.note import Note
from app.models.comment import Comment
from app.models.annotation import Annotation
from app.models.reference import Reference
from app.models.figure import Figure
from app.models.sharelink import ShareLink

def create_all_tables():
    """
    Create all database tables using SQLAlchemy models
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Get database URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("ERROR: DATABASE_URL environment variable is not set.")
            sys.exit(1)
            
        print(f"Using DATABASE_URL: {database_url}")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Create all tables
        print("Creating all tables...")
        Base.metadata.create_all(engine)
        
        print("All tables created successfully!")
        print("The following tables were created:")
        
        # List all table names
        table_names = Base.metadata.tables.keys()
        for table_name in sorted(table_names):
            print(f"  - {table_name}")
            
    except Exception as e:
        print(f"ERROR: Failed to create tables: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_all_tables()