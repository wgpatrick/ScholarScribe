"""
Test script for the direct LlamaCloud client.
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath("."))

# Import our direct client
from app.services.pdf_parsing.direct_llama_client import DirectLlamaClient

# PDF file to parse
pdf_path = "tests/pdf_corpus/papers/cs/attention_is_all_you_need.pdf"

# Parsing instruction (for academic papers)
academic_instruction = """
The provided document is an academic research paper or scientific publication.

Please ensure:
1. Include ALL the original text with no summarization or omissions
2. Preserve the hierarchical structure of sections and subsections exactly as they appear
3. Handle multiple columns properly, maintaining correct reading order
4. Extract tables and figures with their captions in full
5. Format mathematical equations in LaTeX (between $ symbols)
6. Preserve all citations and references exactly as they appear
7. Distinguish between abstract, main content, and footnotes
8. Properly identify section headings and maintain their hierarchy
9. Extract metadata like title, authors, and publication details

IMPORTANT: Do NOT summarize sections or content. Preserve ALL original text verbatim while maintaining structure.
Focus on producing a complete, well-structured conversion that captures every detail of the original document.
"""

# Initialize the client
client = DirectLlamaClient()

# Parse the PDF
logger.info(f"Parsing PDF: {pdf_path}")
result = client.parse_pdf(pdf_path, output_format="markdown", parsing_instruction=academic_instruction)

# Save the result
output_path = "direct_client_output.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(result)

# Check result length
logger.info(f"Output saved to {output_path}")
logger.info(f"Output length: {len(result)} characters")
logger.info(f"Line count: {result.count(chr(10)) + 1}")  # Count newlines + 1 for the last line