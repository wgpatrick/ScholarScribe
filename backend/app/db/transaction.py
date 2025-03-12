from contextlib import contextmanager
from typing import Generator, TypeVar, Callable, Any, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .database import SessionLocal

# Type variable for the transaction result
T = TypeVar('T')

@contextmanager
def transaction() -> Generator[Session, None, None]:
    """
    Context manager for database transactions.
    
    Usage:
    ```
    with transaction() as db:
        # Perform database operations
        # Commits automatically if no exceptions
        # Rolls back on exception
    ```
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def run_in_transaction(func: Callable[..., T], **kwargs) -> T:
    """
    Run a function within a transaction.
    
    Usage:
    ```
    def create_document_with_sections(document_data, sections_data):
        document = document_repository.create(db, obj_in=document_data)
        for section_data in sections_data:
            section_data["document_id"] = document.id
            section_repository.create(db, obj_in=section_data)
        return document
    
    document = run_in_transaction(create_document_with_sections, 
                                 document_data=document_data, 
                                 sections_data=sections_data)
    ```
    """
    with transaction() as db:
        return func(db=db, **kwargs)


class TransactionManager:
    """
    Class to manage transactions with error handling and logging.
    """
    
    @staticmethod
    def execute(
        func: Callable[..., T], 
        error_msg: str = "Database transaction failed", 
        **kwargs
    ) -> Optional[T]:
        """
        Execute a function within a transaction with error handling.
        
        Args:
            func: The function to execute (must accept a 'db' parameter)
            error_msg: Error message to log if transaction fails
            **kwargs: Additional arguments to pass to the function
            
        Returns:
            The result of the function or None if an error occurred
        """
        try:
            return run_in_transaction(func, **kwargs)
        except SQLAlchemyError as e:
            # Log the error (we'll enhance this with proper logging)
            print(f"{error_msg}: {str(e)}")
            return None
        except Exception as e:
            # Log other errors
            print(f"Unexpected error in transaction: {str(e)}")
            return None


# Create a singleton instance
transaction_manager = TransactionManager()