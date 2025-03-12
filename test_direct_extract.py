"""
Extract the actual markdown content from LlamaParse results.
"""
import sys
import json
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Input path to check
input_files = [
    "tests/pdf_corpus/papers/cs/attention_is_all_you_need_llamaparse.md",
    "direct_client_output.md",
    "direct_raw_output.txt"
]

# Process each file
for input_path in input_files:
    try:
        if not os.path.exists(input_path):
            logger.info(f"File not found: {input_path}")
            continue
            
        logger.info(f"Processing file: {input_path}")
        
        # Read file content
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        output_path = f"{input_path}.extracted.md"
        
        # Try to parse as JSON
        if content.startswith("{") and "markdown" in content[:100]:
            logger.info(f"Looks like JSON with markdown field")
            try:
                data = json.loads(content)
                if "markdown" in data:
                    markdown_content = data["markdown"]
                    logger.info(f"Successfully extracted markdown content: {len(markdown_content)} characters")
                    
                    # Save extracted content
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    
                    logger.info(f"Extracted content saved to: {output_path}")
                else:
                    logger.info("No 'markdown' field found in JSON")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse as JSON: {e}")
        else:
            logger.info("File doesn't appear to be JSON with markdown field")
            
            # Check if it starts with # (likely already markdown)
            if content.lstrip().startswith("#"):
                logger.info("Content appears to already be in markdown format")
            else:
                logger.info("Content is in unknown format")
                
    except Exception as e:
        logger.error(f"Error processing {input_path}: {e}")