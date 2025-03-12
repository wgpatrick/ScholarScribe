from fastapi import APIRouter
from .routes import documents, admin

api_router = APIRouter()
api_router.include_router(documents.router, tags=["documents"])
api_router.include_router(admin.router, tags=["admin"])
