from fastapi import APIRouter
from .routes import documents

api_router = APIRouter()
api_router.include_router(documents.router)
