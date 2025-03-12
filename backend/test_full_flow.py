#!/usr/bin/env python
"""
Test script to verify the full document upload → process → retrieve flow

This script tests the complete workflow:
1. Uploads a PDF
2. Waits for processing to complete
3. Retrieves the document with sections, references, and figures
4. Prints the results
"""
import argparse
import asyncio
import os
import requests
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Constants
API_BASE_URL = "http://localhost:8000"  # Update with your API URL

class APIClient:
    """Simple client for testing the API flow"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def upload_document(self, pdf_path: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a document to the API
        
        Args:
            pdf_path: Path to the PDF file
            title: Optional title for the document
            
        Returns:
            Dict: Response from the API
        """
        print(f"Uploading document: {pdf_path}")
        
        files = {'file': open(pdf_path, 'rb')}
        data = {}
        if title:
            data['title'] = title
            
        response = requests.post(
            f"{self.base_url}/documents/", 
            files=files,
            data=data
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to upload document: {response.text}")
            
        return response.json()
    
    async def wait_for_processing(self, document_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
        """
        Wait for document processing to complete
        
        Args:
            document_id: UUID of the document
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            Dict: Document data
        """
        print(f"Waiting for processing to complete for document: {document_id}")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            response = requests.get(f"{self.base_url}/documents/{document_id}")
            
            if response.status_code != 200:
                raise Exception(f"Failed to get document: {response.text}")
                
            document = response.json()
            status = document.get("processing_status")
            
            if status == "completed":
                print(f"Processing completed in {time.time() - start_time:.2f} seconds")
                return document
            elif status == "failed":
                raise Exception(f"Document processing failed: {document}")
                
            print(f"Document status: {status}, waiting...")
            await asyncio.sleep(5)
            
        raise Exception(f"Timed out waiting for document processing after {max_wait_time} seconds")
    
    async def get_document_with_sections(self, document_id: str) -> Dict[str, Any]:
        """
        Get a document with its sections
        
        Args:
            document_id: UUID of the document
            
        Returns:
            Dict: Document with sections
        """
        print(f"Getting document with sections: {document_id}")
        
        response = requests.get(f"{self.base_url}/documents/{document_id}/with-sections")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get document with sections: {response.text}")
            
        return response.json()
    
    async def get_document_references(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get document references
        
        Args:
            document_id: UUID of the document
            
        Returns:
            List[Dict]: References
        """
        print(f"Getting document references: {document_id}")
        
        response = requests.get(f"{self.base_url}/documents/{document_id}/references")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get document references: {response.text}")
            
        return response.json()
    
    async def get_document_figures(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get document figures
        
        Args:
            document_id: UUID of the document
            
        Returns:
            List[Dict]: Figures
        """
        print(f"Getting document figures: {document_id}")
        
        response = requests.get(f"{self.base_url}/documents/{document_id}/figures")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get document figures: {response.text}")
            
        return response.json()


async def run_test(pdf_path: str, title: Optional[str] = None):
    """
    Run the full test flow
    
    Args:
        pdf_path: Path to the PDF file
        title: Optional title for the document
    """
    client = APIClient(API_BASE_URL)
    
    try:
        # 1. Upload document
        document = await client.upload_document(pdf_path, title)
        document_id = document["id"]
        print(f"Document uploaded with ID: {document_id}")
        
        # 2. Wait for processing to complete
        processed_document = await client.wait_for_processing(document_id)
        print(f"Document processing completed")
        
        # 3. Get document with sections
        document_with_sections = await client.get_document_with_sections(document_id)
        sections = document_with_sections.get("sections", [])
        print(f"Retrieved document with {len(sections)} sections")
        
        # Print section tree (just titles)
        print("\nSection Structure:")
        for section in sections:
            print(f"{'  ' * (section['level'] - 1)}• {section['title']}")
            
        # 4. Get references
        references = await client.get_document_references(document_id)
        print(f"\nRetrieved {len(references)} references")
        
        # Print first 3 references
        if references:
            print("\nSample References:")
            for ref in references[:3]:
                print(f"• {ref.get('raw_citation', '')[:100]}...")
        
        # 5. Get figures
        figures = await client.get_document_figures(document_id)
        print(f"\nRetrieved {len(figures)} figures/tables")
        
        # Print figures info
        if figures:
            print("\nFigures and Tables:")
            for fig in figures:
                print(f"• [{fig['figure_type']}] {fig['reference_id']}: {fig.get('caption', '')[:50]}...")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the full document flow")
    parser.add_argument("pdf_path", help="Path to the PDF file to test")
    parser.add_argument("--title", help="Optional title for the document")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found: {args.pdf_path}")
        exit(1)
    
    asyncio.run(run_test(args.pdf_path, args.title))