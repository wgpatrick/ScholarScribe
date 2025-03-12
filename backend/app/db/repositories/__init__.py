from .document_repository import document_repository
from .section_repository import section_repository
from .reference_repository import reference_repository
from .figure_repository import figure_repository

# Export the repositories
__all__ = [
    "document_repository",
    "section_repository",
    "reference_repository",
    "figure_repository"
]