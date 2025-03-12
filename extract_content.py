"""
Extract markdown content from LlamaParse API response.
"""
import json
import sys

# Read the JSON response file
with open("direct_job_result.md", "r") as f:
    json_text = f.read()

# Parse the JSON to extract the markdown content
try:
    data = json.loads(json_text)
    markdown_content = data.get("markdown", "")
    
    # Save the markdown content
    with open("extracted_content.md", "w") as f:
        f.write(markdown_content)
    
    print(f"Extracted markdown content (length: {len(markdown_content)} characters)")
    print(f"Saved to extracted_content.md")
    
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
    sys.exit(1)