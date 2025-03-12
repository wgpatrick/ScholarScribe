"""
Test fixtures for database testing
"""
import os
import pytest
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from app.db.database import Base
from app.models.document import Document
from app.models.section import Section
from app.models.reference import Reference
from app.models.figure import Figure
from app.models.note import Note
from app.models.comment import Comment
from app.models.annotation import Annotation
from app.models.sharelink import ShareLink

# Test database configuration
TEST_DATABASE_URL = "postgresql://willpatrick@localhost:5432/test_scholarscribe"

@pytest.fixture(scope="session")
def engine():
    """
    Create a SQLAlchemy engine for the test database
    """
    # Create a unique test database for this test run
    pg_url = "postgresql://willpatrick@localhost:5432/postgres"
    temp_engine = create_engine(pg_url)
    conn = temp_engine.connect()
    conn.execute(text("COMMIT"))
    
    # Drop the test database if it exists and recreate it
    conn.execute(text(f"DROP DATABASE IF EXISTS test_scholarscribe"))
    conn.execute(text(f"CREATE DATABASE test_scholarscribe"))
    conn.close()
    temp_engine.dispose()
    
    # Connect to the test database
    engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup - drop all tables and close connection
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def db_session(engine):
    """
    Create a new database session for a test
    
    This fixture provides a session for each test that will automatically
    roll back any changes after the test is done.
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(bind=connection)
    session = Session()
    
    # Ensure we start with a clean session for each test
    session.begin_nested()
    
    yield session
    
    # Rollback all changes after the test
    session.close()
    transaction.rollback()
    connection.close()