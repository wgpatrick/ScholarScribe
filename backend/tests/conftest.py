"""
Test fixtures for database testing
"""
import os
import pytest
from sqlalchemy import create_engine
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

@pytest.fixture(scope="session")
def database_url(postgresql_proc):
    """
    Create a PostgreSQL database URL from pytest-postgresql fixture
    """
    return f"postgresql://postgres:postgres@{postgresql_proc.host}:{postgresql_proc.port}/postgres"

@pytest.fixture(scope="session")
def engine(database_url):
    """
    Create a SQLAlchemy engine for the test database
    """
    engine = create_engine(database_url, poolclass=NullPool)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def create_tables(engine):
    """
    Create all database tables for testing
    """
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, create_tables):
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