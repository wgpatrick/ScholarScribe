from sqlalchemy.orm import Session
import asyncio
import logging
import os
from typing import Optional, Dict, List, Tuple
import re
from dotenv import load_dotenv

from ..models.document import Document
from .pdf_parsing.llama_parse_client import LlamaParseClient
from .pdf_parsing.academic_parser import AcademicPaperParser

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class PDFConverterService:
    """Service for converting PDFs to structured markdown"""
    
    def __init__(self):
        """Initialize the converter service with parsers."""
        # Check if we have a Replicate API token
        if os.environ.get("REPLICATE_API_TOKEN"):
            self.llama_parse_client = LlamaParseClient()
        else:
            self.llama_parse_client = None
            logger.warning(
                "REPLICATE_API_TOKEN not found in environment. "
                "LlamaParse integration disabled."
            )
    
    async def convert_pdf_to_markdown(self, document_id: int, db: Session):
        """
        Convert a PDF document to structured markdown
        
        Args:
            document_id: ID of the document to convert
            db: Database session
        """
        try:
            # Get the document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"Document not found: {document_id}")
                return
            
            # Update status to processing
            document.conversion_status = "processing"
            db.commit()
            
            # Get the PDF path
            pdf_path = document.pdf_path
            
            # Process the PDF - try LlamaParse first, fall back to custom parser
            try:
                if self.llama_parse_client:
                    # Try using LlamaParse
                    try:
                        logger.info(f"Using LlamaParse to convert document {document_id}")
                        markdown_text = self.llama_parse_client.parse_pdf(pdf_path)
                        
                        # Extract metadata if needed
                        metadata = self.llama_parse_client.extract_metadata(markdown_text)
                        
                        # Update the document
                        document.markdown_text = markdown_text
                        document.conversion_status = "completed"
                        
                        # Update title if extracted
                        if metadata.get("title") and metadata["title"] \!= document.title:
                            document.title = metadata["title"]
                        
                        db.commit()
                        logger.info(f"Successfully converted document {document_id} with LlamaParse")
                        return
                        
                    except Exception as e:
                        logger.error(f"LlamaParse error: {str(e)}, falling back to custom parser")
                
                # Fall back to custom parser
                logger.info(f"Using custom parser for document {document_id}")
                custom_parser = AcademicPaperParser(pdf_path)
                markdown_text = custom_parser.process()
                
                # Update the document with the markdown text
                document.markdown_text = markdown_text
                document.conversion_status = "completed"
                
                # Update title if extracted
                if custom_parser.metadata.get("title") and custom_parser.metadata["title"] \!= document.title:
                    document.title = custom_parser.metadata["title"]
                
                db.commit()
                logger.info(f"Successfully converted document {document_id} with custom parser")
            
            except Exception as e:
                logger.error(f"Error converting PDF: {str(e)}")
                document.conversion_status = "failed"
                db.commit()
        
        except Exception as e:
            logger.error(f"Error in conversion process: {str(e)}")
            try:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.conversion_status = "failed"
                    db.commit()
            except:
                pass
