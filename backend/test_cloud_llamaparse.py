"""
Test script for directly using LlamaCloud services.
"""
import os
import json
import nest_asyncio
from llama_cloud_services import LlamaParse
from dotenv import load_dotenv

# Apply nest_asyncio for Jupyter-like environments
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# PDF file to parse
pdf_file = "tests/pdf_corpus/papers/cs/attention_is_all_you_need.pdf"

# Parse the PDF
documents = LlamaParse(result_type="markdown").load_data(pdf_file)

# Check the result
if documents:
    print(f"Parsing successful, document length: {len(documents[0].text)} characters")
    
    # Save the output
    output_path = "attention_cloud_output.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(documents[0].text)
    
    print(f"Output saved to {output_path}")
else:
    print("No documents returned")