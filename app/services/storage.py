import os
import shutil
from pathlib import Path
from fastapi import UploadFile
from dotenv import load_dotenv
from uuid import uuid4

# Load environment variables
load_dotenv()

STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "./storage/uploads")

class StorageService:
    """Service for handling file storage operations"""
    
    def __init__(self):
        """Initialize the storage service based on configuration"""
        if STORAGE_TYPE == "local":
            self.storage_path = Path(LOCAL_STORAGE_PATH)
            os.makedirs(self.storage_path, exist_ok=True)
        elif STORAGE_TYPE == "s3":
            # Configure S3 when we implement it
            pass
        else:
            raise ValueError(f"Unsupported storage type: {STORAGE_TYPE}")
    
    async def save_pdf(self, file: UploadFile) -> str:
        """
        Save a PDF file to storage and return the path
        
        Args:
            file: The uploaded PDF file
            
        Returns:
            str: The path where the file is saved
        """
        if STORAGE_TYPE == "local":
            return await self._save_local(file)
        elif STORAGE_TYPE == "s3":
            # Implement S3 storage later
            pass
    
    async def _save_local(self, file: UploadFile) -> str:
        """Save a file to local storage"""
        # Generate a unique filename
        filename = f"{uuid4()}.pdf"
        file_path = self.storage_path / filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return str(file_path)
    
    def get_file_path(self, path: str) -> str:
        """Get the full path to a file"""
        if STORAGE_TYPE == "local":
            return path
        elif STORAGE_TYPE == "s3":
            # Implement S3 URL generation later
            pass
