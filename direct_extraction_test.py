"""
Test script that directly accesses the LlamaCloud API and extracts raw markdown content.
"""
import os
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
if not api_key:
    raise ValueError("LLAMA_CLOUD_API_KEY not found in environment variables")

# API endpoints
UPLOAD_URL = "https://api.cloud.llamaindex.ai/api/parsing/upload"

# Headers for requests
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# PDF file to parse
pdf_path = "tests/pdf_corpus/papers/cs/attention_is_all_you_need.pdf"

# Step 1: Upload the file to start a parsing job
print("Uploading file to LlamaCloud...")
with open(pdf_path, 'rb') as file:
    upload_files = {
        'file': (os.path.basename(pdf_path), file, 'application/pdf')
    }
    
    # Use no custom instructions to get raw output
    data = {}
    
    upload_response = requests.post(
        UPLOAD_URL,
        headers=headers,
        files=upload_files,
        data=data,
        timeout=120  # 2 minute timeout for upload
    )
    
    upload_response.raise_for_status()
    upload_result = upload_response.json()
    
    # Extract job ID from the response
    job_id = upload_result.get('id')
    if not job_id:
        raise ValueError("No job ID returned from upload")
    
    print(f"File uploaded successfully. Job ID: {job_id}")

# Step 2: Poll for job status until complete
print("Waiting for parsing to complete...")
status_url = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}"

max_polls = 30
poll_interval = 2
for i in range(max_polls):
    print(f"Polling job status ({i+1}/{max_polls})...")
    
    status_response = requests.get(
        status_url,
        headers=headers,
        timeout=30
    )
    
    status_response.raise_for_status()
    status_result = status_response.json()
    
    print(f"Job status: {status_result.get('status')}")
    
    if status_result.get('status') in ['SUCCESS', 'completed']:
        print("Parsing job completed successfully")
        break
    elif status_result.get('status') in ['failed', 'error', 'FAILED']:
        error_message = status_result.get('error', 'Unknown error')
        raise ValueError(f"Parsing job failed: {error_message}")
    
    # If still processing, wait and try again
    if i < max_polls - 1:
        time.sleep(poll_interval)
else:
    # If we get here, we've exceeded max polls
    raise ValueError(f"Parsing job timed out after {max_polls * poll_interval} seconds")

# Step 3: Retrieve the markdown results
print("Retrieving parsing results in markdown format...")
result_url = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/markdown"

result_response = requests.get(
    result_url,
    headers=headers,
    timeout=60
)

result_response.raise_for_status()

# Save the raw response first
raw_output_path = "direct_raw_output.txt"
with open(raw_output_path, "wb") as f:
    f.write(result_response.content)

print(f"Raw API response saved to {raw_output_path}")

# Try to parse as JSON and extract markdown content
try:
    data = result_response.json()
    if isinstance(data, dict) and "markdown" in data:
        markdown_content = data["markdown"]
        
        # Save the extracted markdown content
        markdown_output_path = "direct_markdown_output.md"
        with open(markdown_output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        print(f"Markdown content extracted successfully and saved to {markdown_output_path}")
        print(f"Markdown content length: {len(markdown_content)} characters")
    else:
        print("Response is valid JSON but does not contain a 'markdown' field")
except (json.JSONDecodeError, ValueError):
    print("Response is not valid JSON, saving raw content as markdown")
    
    # Save the raw content as markdown
    markdown_output_path = "direct_raw_content.md"
    with open(markdown_output_path, "w", encoding="utf-8") as f:
        f.write(result_response.text)
    
    print(f"Raw content saved to {markdown_output_path}")