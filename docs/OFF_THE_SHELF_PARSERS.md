# Off-the-Shelf Academic Paper Parsing Solutions

## Overview

Rather than building our custom academic paper parser from scratch, several specialized tools already exist that are designed specifically for parsing academic papers. This document outlines options for integrating these solutions into our application.

## Available Solutions

### 1. LlamaParse

**Description:** LlamaParse is Meta's document parsing tool designed for extracting structured content from PDFs, with specific optimizations for academic papers.

**Key Features:**
- Handles multi-column layouts correctly
- Preserves document structure (headings, sections, paragraphs)
- Extracts tables and figures with captions
- Maintains mathematical notation
- Identifies reference sections and citations
- Retains formatting information

**Integration Options:**
- API access through Anthropic, Replicate or other providers
- Direct Python client if available

### 2. Unstructured.io

**Description:** An open-source document parsing library that handles PDFs and other document formats.

**Key Features:**
- Extracts structured content from PDFs
- Handles tables and layouts
- Provides metadata extraction
- Open-source with active development

**Integration Options:**
- Direct Python library integration
- Self-hosted API
- Managed API service

### 3. Sensible

**Description:** Document extraction API specialized in converting PDFs to structured data.

**Key Features:**
- Highly accurate PDF parsing
- Configurable extraction rules
- Handles complex layouts
- API service

### 4. PyMuPDF + PaperScraper

**Description:** PaperScraper is built on top of PyMuPDF specifically for academic papers.

**Key Features:**
- Open-source
- Specialized for research papers
- Extracts metadata, sections, and references

## Integration Approach

For our application, we recommend the following integration approach:

1. **Primary Option: LlamaParse**
   - Most specialized for academic papers
   - Likely to handle all our requirements out of the box
   - Integration via API

2. **Fallback Option: Unstructured.io**
   - Open-source alternative
   - Direct Python integration possible
   - May require more customization for academic papers

## Implementation Plan

### 1. LlamaParse Integration

```python
# Example pseudocode for LlamaParse integration
import requests

class LlamaParseConverter:
    """Convert PDFs to structured Markdown using LlamaParse API."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_endpoint = "https://api.llamaparse.ai/v1/parse"
        
    def convert_pdf_to_markdown(self, pdf_path):
        """
        Convert PDF to structured Markdown using LlamaParse.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            str: Structured Markdown representation
        """
        with open(pdf_path, "rb") as file:
            files = {"file": file}
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.post(
                self.api_endpoint,
                files=files,
                headers=headers,
                params={"format": "markdown", "type": "academic_paper"}
            )
            
            if response.status_code == 200:
                return response.json()["markdown"]
            else:
                raise Exception(f"LlamaParse API error: {response.text}")
```

### 2. Integration into Existing System

Our PDF converter service would be updated to use the off-the-shelf parser:

```python
from sqlalchemy.orm import Session
import logging

from ..models.document import Document
from .llama_parse_converter import LlamaParseConverter

logger = logging.getLogger(__name__)

class PDFConverterService:
    """Service for converting PDFs to structured markdown"""
    
    def __init__(self, api_key):
        self.converter = LlamaParseConverter(api_key)
    
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
            
            # Convert using LlamaParse
            try:
                markdown_text = self.converter.convert_pdf_to_markdown(pdf_path)
                
                # Update the document with the markdown text
                document.markdown_text = markdown_text
                document.conversion_status = "completed"
                
                # We could also extract metadata from the response if needed
                
                db.commit()
                
                logger.info(f"Successfully converted document {document_id}")
            
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
```

### 3. Fallback Strategy

If the primary parser fails, we can implement a fallback strategy:

```python
# First try LlamaParse
try:
    markdown_text = self.llamaparse_converter.convert_pdf_to_markdown(pdf_path)
except Exception as e:
    logger.warning(f"LlamaParse conversion failed: {str(e)}, trying fallback...")
    try:
        # Fallback to Unstructured.io
        markdown_text = self.unstructured_converter.convert_pdf_to_markdown(pdf_path)
    except Exception as e2:
        logger.error(f"Fallback conversion also failed: {str(e2)}")
        # Final fallback to our basic converter
        markdown_text = self.basic_converter.convert_pdf_to_markdown(pdf_path)
```

## Cost Considerations

Using third-party API services will have associated costs:

1. **LlamaParse API**:
   - Per-document pricing likely based on page count
   - May have monthly subscription tiers
   - API rate limits to consider

2. **Self-hosted alternatives**:
   - Higher upfront development time
   - Lower per-document cost
   - More maintenance required

For an MVP with relatively low volume, the API approach provides the quickest path to a high-quality solution.

## Next Steps

1. Research specific API access options for LlamaParse
2. Set up API keys and test with a sample document
3. Implement the integration in our PDF converter service
4. Add error handling and fallback options
5. Update tests to work with the new parser integration
