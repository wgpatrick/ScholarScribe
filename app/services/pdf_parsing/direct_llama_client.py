"""
Direct LlamaCloud API client for PDF parsing.

This implementation directly uses the HTTP API to parse PDFs with full content extraction.
"""
import os
import time
import logging
import json
import requests
from typing import Optional

# Setup logging
logger = logging.getLogger(__name__)

class DirectLlamaClient:
    """Client for directly accessing the LlamaCloud API for PDF parsing."""
    
    # LlamaCloud API endpoints for document parsing
    LLAMACLOUD_UPLOAD_URL = "https://api.cloud.llamaindex.ai/api/parsing/upload"
    LLAMACLOUD_JOB_STATUS_URL = "https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}"
    LLAMACLOUD_RESULT_URL = "https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/{format}"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the client.
        
        Args:
            api_key: LlamaCloud API key. If not provided, will look for 
                   LLAMA_CLOUD_API_KEY in environment variables.
        """
        self.api_key = api_key or os.environ.get("LLAMA_CLOUD_API_KEY")
        if not self.api_key:
            raise ValueError("LlamaCloud API key is required. Provide it or set LLAMA_CLOUD_API_KEY environment variable.")
    
    def parse_pdf(self, pdf_path: str, output_format: str = "markdown", parsing_instruction: Optional[str] = None):
        """
        Parse a PDF file using the LlamaCloud API directly.
        
        Args:
            pdf_path: Path to the PDF file to parse
            output_format: Output format ("markdown", "json", or "html")
            parsing_instruction: Optional instructions to guide the parsing process
            
        Returns:
            str: Parsed content in the requested format
        """
        logger.info(f"Parsing PDF with DirectLlamaClient: {pdf_path}")
        start_time = time.time()
        
        # Headers for requests
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Step 1: Upload the file to start a parsing job
        logger.info("Uploading file to LlamaCloud...")
        
        with open(pdf_path, 'rb') as file:
            upload_files = {
                'file': (os.path.basename(pdf_path), file, 'application/pdf')
            }
            
            # Add parsing instruction if provided
            data = {}
            if parsing_instruction:
                logger.info(f"Using parsing instruction: {parsing_instruction[:50]}...")
                data['parsing_instruction'] = parsing_instruction
            
            # Log the exact request details
            logger.info(f"API URL: {self.LLAMACLOUD_UPLOAD_URL}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Files: {upload_files.keys()}")
            logger.info(f"Data parameters: {data.keys()}")
            
            upload_response = requests.post(
                self.LLAMACLOUD_UPLOAD_URL,
                headers=headers,
                files=upload_files,
                data=data,
                timeout=120  # 2 minute timeout for upload
            )
            
            # Log the API response details
            logger.info(f"Upload response status: {upload_response.status_code}")
            logger.info(f"Upload response headers: {dict(upload_response.headers)}")
            
            upload_response.raise_for_status()
            upload_result = upload_response.json()
            
            # Extract job ID from the response
            job_id = upload_result.get('id')
            if not job_id:
                raise ValueError("No job ID returned from upload")
            
            logger.info(f"File uploaded successfully. Job ID: {job_id}")
        
        # Step 2: Poll for job status until complete
        logger.info("Waiting for parsing to complete...")
        status_url = self.LLAMACLOUD_JOB_STATUS_URL.format(job_id=job_id)
        
        max_polls = 30
        poll_interval = 2
        for i in range(max_polls):
            logger.info(f"Polling job status ({i+1}/{max_polls})...")
            
            # Log the status request details
            logger.info(f"Status check URL: {status_url}")
            
            status_response = requests.get(
                status_url,
                headers=headers,
                timeout=30
            )
            
            # Log the response details
            logger.info(f"Status response code: {status_response.status_code}")
            
            status_response.raise_for_status()
            status_result = status_response.json()
            
            # Log status result details
            logger.info(f"Status result: {status_result}")
            
            status = status_result.get('status')
            if status in ['SUCCESS', 'completed']:
                logger.info("Parsing job completed successfully")
                break
            elif status in ['failed', 'error', 'FAILED']:
                error_message = status_result.get('error', 'Unknown error')
                raise ValueError(f"Parsing job failed: {error_message}")
            
            # If still processing, wait and try again
            if i < max_polls - 1:
                time.sleep(poll_interval)
        else:
            # If we get here, we've exceeded max polls
            raise ValueError(f"Parsing job timed out after {max_polls * poll_interval} seconds")
        
        # Step 3: Retrieve the results in the requested format
        logger.info(f"Retrieving parsing results in {output_format} format...")
        result_url = self.LLAMACLOUD_RESULT_URL.format(job_id=job_id, format=output_format)
        
        # Log the result request details
        logger.info(f"Result retrieval URL: {result_url}")
        
        result_response = requests.get(
            result_url,
            headers=headers,
            timeout=60
        )
        
        # Log response details
        logger.info(f"Result response status: {result_response.status_code}")
        logger.info(f"Result response headers: {dict(result_response.headers)}")
        logger.info(f"Result content type: {result_response.headers.get('Content-Type')}")
        logger.info(f"Result content length: {result_response.headers.get('Content-Length')} bytes")
        
        result_response.raise_for_status()
        
        # Process the response based on the format
        if output_format == "json":
            # Return JSON as string
            result = json.dumps(result_response.json(), indent=2)
        else:
            # For markdown and HTML, extract from JSON if needed
            try:
                data = result_response.json()
                logger.info(f"Response data type: {type(data)}, keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
                
                if isinstance(data, dict) and output_format in data:
                    # Extract content from the appropriate field
                    logger.info(f"Extracting content from '{output_format}' field")
                    result = data[output_format]
                elif isinstance(data, dict) and "markdown" in data and output_format == "markdown":
                    # Handle old API format
                    logger.info("Extracting content from 'markdown' field")
                    result = data["markdown"]
                else:
                    # Log the actual data structure for debugging
                    logger.warning(f"Could not find expected field in response. Response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                    
                    # Check if the data itself is a string (might be directly the content)
                    if isinstance(data, str) and len(data) > 10:  # Assuming content should be longer than 10 chars
                        logger.info("Response data is a string, using as result")
                        result = data
                    else:
                        # Fall back to raw response
                        logger.warning("Falling back to raw JSON response")
                        result = json.dumps(data, indent=2)
                
                # Clean up the result by removing LLM commentary lines
                if isinstance(result, str) and output_format in ["markdown", "text"]:
                    # Remove lines like "I'm sorry, but I can't assist with that"
                    lines = result.split("\n")
                    cleaned_lines = []
                    skip_section = False
                    
                    for line in lines:
                        # Skip lines containing LLM refusal or commentary patterns
                        if any(pattern in line.lower() for pattern in [
                            "i'm sorry",
                            "i can't assist",
                            "i cannot assist",
                            "i apologize",
                            "can't help",
                            "cannot help"
                        ]):
                            skip_section = True
                            continue
                            
                        # Reset skip_section when we hit a section separator or heading
                        if line.strip() == "---" or line.startswith("#"):
                            skip_section = False
                        
                        # Only add line if we're not in a skip section
                        if not skip_section:
                            cleaned_lines.append(line)
                    
                    # Reassemble the cleaned content
                    result = "\n".join(cleaned_lines)
                    logger.info(f"Cleaned result: removed {len(lines) - len(cleaned_lines)} problematic lines")
                
                # Log the result length
                logger.info(f"Result length: {len(result)} characters, line count: {result.count(chr(10)) + 1}")
            
            except (json.JSONDecodeError, ValueError):
                # Not JSON, return raw text
                logger.info("Response is not JSON, using raw text")
                result = result_response.text
                logger.info(f"Raw text length: {len(result)} characters")
        
        processing_time = time.time() - start_time
        logger.info(f"PDF parsing completed in {processing_time:.2f} seconds")
        
        return result