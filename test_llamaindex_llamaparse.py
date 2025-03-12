"""
Test script for using LlamaParse via LlamaIndex.
"""
import os
import json
import nest_asyncio
from llama_index.readers.file import PDFReader
from dotenv import load_dotenv

# Apply nest_asyncio for Jupyter-like environments
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
if not api_key:
    raise ValueError("LLAMA_CLOUD_API_KEY not found in environment variables")

# PDF file to parse
pdf_file = "tests/pdf_corpus/papers/cs/attention_is_all_you_need.pdf"

# Parse with PDFReader which uses LlamaParse by default
loader = PDFReader()
documents = loader.load_data(pdf_file)

# Check the result
if documents:
    print(f"Parsing successful, document length: {len(documents[0].text)} characters")
    
    # Save the output
    output_path = "attention_llamaindex_output.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(documents[0].text)
    
    print(f"Output saved to {output_path}")
else:
    print("No documents returned")