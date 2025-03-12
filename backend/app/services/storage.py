import os
import shutil
import hashlib
import boto3
import logging
from botocore.exceptions import ClientError
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import Dict, Optional, BinaryIO, Tuple, Any
from dotenv import load_dotenv
from uuid import uuid4

# Load environment variables
load_dotenv()

# Configuration
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "./storage/uploads")
S3_BUCKET = os.getenv("S3_BUCKET", "scholarscribe-documents")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")  # For LocalStack support

# Configure logging
logger = logging.getLogger(__name__)

class StorageException(Exception):
    """Exception raised for storage service errors"""
    pass

class StorageService:
    """
    Service for handling file storage operations with support for both
    local filesystem and S3 storage
    """
    
    def __init__(self):
        """Initialize the storage service based on configuration"""
        self.storage_type = STORAGE_TYPE
        
        if self.storage_type == "local":
            self.storage_path = Path(LOCAL_STORAGE_PATH)
            os.makedirs(self.storage_path, exist_ok=True)
            logger.info(f"Using local storage at {self.storage_path}")
        elif self.storage_type == "s3":
            # Configure S3 client
            s3_kwargs = {}
            if S3_ENDPOINT_URL:
                # For LocalStack or custom S3-compatible storage
                s3_kwargs["endpoint_url"] = S3_ENDPOINT_URL
            
            self.s3_client = boto3.client("s3", **s3_kwargs)
            self.s3_bucket = S3_BUCKET
            
            logger.info(f"Using S3 storage with bucket {self.s3_bucket}")
            
            # Check if bucket exists
            try:
                self.s3_client.head_bucket(Bucket=self.s3_bucket)
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                if error_code == "404":
                    # Bucket doesn't exist, create it
                    try:
                        self.s3_client.create_bucket(Bucket=self.s3_bucket)
                        logger.info(f"Created S3 bucket: {self.s3_bucket}")
                    except ClientError as ce:
                        logger.error(f"Failed to create S3 bucket: {ce}")
                        raise StorageException(f"Failed to create S3 bucket: {ce}")
                else:
                    logger.error(f"Error connecting to S3: {e}")
                    raise StorageException(f"Error connecting to S3: {e}")
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    async def save_file(
        self, 
        file: UploadFile, 
        directory: str = "documents",
        custom_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save a file to storage and return metadata
        
        Args:
            file: The uploaded file
            directory: Subdirectory to save the file in
            custom_filename: Optional custom filename
            
        Returns:
            Dict with file metadata: path, filename, size, hash
        """
        try:
            # Reset file pointer to beginning for reading
            file.file.seek(0)
            
            # Generate file hash for integrity check
            file_hash = await self._calculate_file_hash(file)
            
            # Reset file pointer again
            file.file.seek(0)
            
            # Get file size
            file_size = await self._get_file_size(file)
            
            # Generate filename if not provided
            if not custom_filename:
                ext = os.path.splitext(file.filename)[1] if file.filename else ""
                filename = f"{uuid4()}{ext}"
            else:
                filename = custom_filename
            
            # Save the file based on storage type
            if self.storage_type == "local":
                file_path = await self._save_local(file, directory, filename)
            elif self.storage_type == "s3":
                file_path = await self._save_s3(file, directory, filename)
                
            return {
                "path": file_path,
                "filename": filename,
                "size": file_size,
                "hash": file_hash
            }
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise StorageException(f"Failed to save file: {str(e)}")
    
    async def save_pdf(self, file: UploadFile) -> Dict[str, Any]:
        """
        Save a PDF file to storage and return metadata
        
        Args:
            file: The uploaded PDF file
            
        Returns:
            Dict with file metadata: path, filename, size, hash
        """
        # Validate that this is a PDF file
        content_type = file.content_type or ""
        if not content_type.lower().endswith("pdf") and not (file.filename and file.filename.lower().endswith(".pdf")):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Save with .pdf extension regardless of original filename
        return await self.save_file(file, directory="documents", custom_filename=f"{uuid4()}.pdf")
    
    async def _save_local(self, file: UploadFile, directory: str, filename: str) -> str:
        """
        Save a file to local storage
        
        Args:
            file: The file to save
            directory: The subdirectory to save to
            filename: The filename to use
            
        Returns:
            str: The path to the saved file
        """
        # Create directory if it doesn't exist
        dir_path = self.storage_path / directory
        os.makedirs(dir_path, exist_ok=True)
        
        # Create file path
        file_path = dir_path / filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return str(file_path)
    
    async def _save_s3(self, file: UploadFile, directory: str, filename: str) -> str:
        """
        Save a file to S3
        
        Args:
            file: The file to save
            directory: The subdirectory/prefix to use
            filename: The filename to use
            
        Returns:
            str: The S3 key for the saved file
        """
        # Create S3 key
        s3_key = f"{directory}/{filename}" if directory else filename
        
        # Upload to S3
        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.s3_bucket,
                s3_key
            )
            return s3_key
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            raise StorageException(f"Error uploading to S3: {e}")
    
    async def delete_file(self, path: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            path: The path or key to the file
            
        Returns:
            bool: True if deletion succeeded, False otherwise
        """
        try:
            if self.storage_type == "local":
                if os.path.exists(path):
                    os.remove(path)
                    return True
                return False
            elif self.storage_type == "s3":
                self.s3_client.delete_object(
                    Bucket=self.s3_bucket,
                    Key=path
                )
                return True
        except Exception as e:
            logger.error(f"Failed to delete file {path}: {str(e)}")
            return False
    
    def get_file_url(self, path: str, expires_in: int = 3600) -> str:
        """
        Get a URL to access the file
        
        Args:
            path: The path or key to the file
            expires_in: URL expiration time in seconds (for S3)
            
        Returns:
            str: The URL to access the file
        """
        if self.storage_type == "local":
            # For local files, just return the path for now
            # In a real app, you might want to serve through a route
            return f"file://{path}"
        elif self.storage_type == "s3":
            # Generate a presigned URL for S3
            try:
                url = self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": self.s3_bucket,
                        "Key": path
                    },
                    ExpiresIn=expires_in
                )
                return url
            except ClientError as e:
                logger.error(f"Error generating URL for {path}: {e}")
                raise StorageException(f"Error generating URL for {path}: {e}")
    
    async def get_file_stream(self, path: str) -> Tuple[BinaryIO, int]:
        """
        Get a file stream for reading
        
        Args:
            path: The path or key to the file
            
        Returns:
            Tuple with file stream and size
        """
        if self.storage_type == "local":
            try:
                file_size = os.path.getsize(path)
                return open(path, "rb"), file_size
            except Exception as e:
                logger.error(f"Error opening file {path}: {e}")
                raise StorageException(f"Error opening file {path}: {e}")
        elif self.storage_type == "s3":
            try:
                response = self.s3_client.get_object(
                    Bucket=self.s3_bucket,
                    Key=path
                )
                return response["Body"], response["ContentLength"]
            except ClientError as e:
                logger.error(f"Error retrieving file from S3 {path}: {e}")
                raise StorageException(f"Error retrieving file from S3 {path}: {e}")
    
    async def _calculate_file_hash(self, file: UploadFile) -> str:
        """
        Calculate SHA-256 hash of a file
        
        Args:
            file: The file to hash
            
        Returns:
            str: Hex-encoded SHA-256 hash
        """
        # Reset file pointer to beginning
        current_position = file.file.tell()
        file.file.seek(0)
        
        # Calculate hash
        sha256_hash = hashlib.sha256()
        chunk_size = 4096
        
        data = await file.read(chunk_size)
        while data:
            sha256_hash.update(data)
            data = await file.read(chunk_size)
        
        # Reset file pointer back to original position
        file.file.seek(current_position)
        
        return sha256_hash.hexdigest()
    
    async def _get_file_size(self, file: UploadFile) -> int:
        """
        Get the size of a file in bytes
        
        Args:
            file: The file to check
            
        Returns:
            int: File size in bytes
        """
        # For FastAPI UploadFile in Python 3.13, we need a different approach
        # First, save the current position
        current_position = file.file.tell()
        
        # Go to the beginning
        file.file.seek(0, os.SEEK_END)
        
        # Get size
        size = file.file.tell()
        
        # Reset file pointer back to original position
        file.file.seek(current_position)
        
        return size

# Create a singleton instance
storage_service = StorageService()
