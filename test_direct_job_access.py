"""
Test script for directly accessing a specific LlamaParse job.
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
if not api_key:
    raise ValueError("LLAMA_CLOUD_API_KEY not found in environment variables")

# Job ID to check (from one of the previous tests)
job_id = "dc8b1abc-986b-4d47-ad0f-d85877a0aead"  # Replace with an actual job ID from previous runs

# API endpoints
JOB_STATUS_URL = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}"
RESULT_URL = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/markdown"

# Headers for requests
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Check job status
print(f"Checking job status for job_id: {job_id}")
status_response = requests.get(JOB_STATUS_URL, headers=headers)
status_response.raise_for_status()
status_data = status_response.json()
print(f"Job status: {status_data.get('status')}")

# If job is completed, get results
if status_data.get('status') in ['completed', 'SUCCESS']:
    print("Retrieving results...")
    result_response = requests.get(RESULT_URL, headers=headers)
    result_response.raise_for_status()
    
    # Save the full result
    output_path = "direct_job_result.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result_response.text)
    
    # Check length and content
    content = result_response.text
    print(f"Result length: {len(content)} characters")
    
    # Check for page separators
    page_separator = "\n---\n"
    pages = content.split(page_separator)
    print(f"Number of pages detected: {len(pages)}")
    
    # Print beginning of each page (up to 3)
    for i, page in enumerate(pages[:3]):
        print(f"\nPage {i+1} preview (first 100 chars):")
        print(page[:100] + "...")
    
    print(f"\nFull result saved to {output_path}")
else:
    print(f"Job is not completed. Status: {status_data.get('status')}")