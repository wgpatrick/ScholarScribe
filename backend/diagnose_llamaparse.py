"""
Diagnostic script for LlamaParse output.

This script tests both the official LlamaParse client and our DirectLlamaClient
to check for potential truncation issues.
"""
import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath("."))

# Check for API key
api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
if not api_key:
    logger.error("LLAMA_CLOUD_API_KEY not found in environment variables")
    sys.exit(1)

# Test PDF file
pdf_path = "tests/pdf_corpus/papers/cs/attention_is_all_you_need.pdf"
if not os.path.exists(pdf_path):
    logger.error(f"Test PDF not found: {pdf_path}")
    # Try to find an alternative PDF
    test_pdfs = list(Path("tests").glob("**/*.pdf"))
    if test_pdfs:
        pdf_path = str(test_pdfs[0])
        logger.info(f"Using alternative PDF: {pdf_path}")
    else:
        logger.error("No test PDFs found")
        sys.exit(1)

# Create output directory
output_dir = Path("llamaparse_diagnosis")
output_dir.mkdir(exist_ok=True)

# Test 1: Official LlamaParse client
logger.info("=== Test 1: Official LlamaParse Client ===")
try:
    from llama_parse import LlamaParse
    import nest_asyncio
    
    # Apply nest_asyncio for Jupyter-like environments
    nest_asyncio.apply()
    
    # Create parser
    parser = LlamaParse(
        api_key=api_key,
        result_type="markdown",
        verbose=True
    )
    
    # Parse the PDF
    logger.info(f"Parsing PDF: {pdf_path}")
    documents = parser.load_data(pdf_path)
    
    # Check the result
    if documents:
        content = documents[0].text
        logger.info(f"Parsing successful, document length: {len(content)} characters")
        logger.info(f"Line count: {content.count(chr(10)) + 1}")
        
        # Check if content is JSON
        if content.startswith('{') and content.endswith('}'):
            try:
                data = json.loads(content)
                logger.info(f"Content is JSON with keys: {list(data.keys())}")
                if "markdown" in data:
                    extracted = data["markdown"]
                    logger.info(f"Extracted markdown length: {len(extracted)} characters")
                    content = extracted
            except json.JSONDecodeError:
                logger.info("Content appears to be JSON but could not be parsed")
        
        # Save the output
        output_path = output_dir / "official_client_output.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Output saved to {output_path}")
    else:
        logger.error("No documents returned")
except Exception as e:
    logger.error(f"Error testing official client: {str(e)}")

# Test 2: Direct LlamaCloud client
logger.info("\n\n=== Test 2: DirectLlamaClient ===")
try:
    from app.services.pdf_parsing.direct_llama_client import DirectLlamaClient
    
    # Parsing instruction 
    academic_instruction = """
    The provided document is an academic research paper. Extract ALL original text with NO summarization.
    Preserve sections, tables, figures, equations, and references exactly as they appear.
    Do not truncate or omit ANY content. Keep the exact structure and organization of the paper.
    """
    
    # Initialize the client
    client = DirectLlamaClient(api_key=api_key)
    
    # Parse the PDF
    logger.info(f"Parsing PDF: {pdf_path}")
    result = client.parse_pdf(pdf_path, output_format="markdown", parsing_instruction=academic_instruction)
    
    # Check the result
    logger.info(f"Parsing successful, result length: {len(result)} characters")
    logger.info(f"Line count: {result.count(chr(10)) + 1}")
    
    # Save the result
    output_path = output_dir / "direct_client_output.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    
    logger.info(f"Output saved to {output_path}")
except Exception as e:
    logger.error(f"Error testing direct client: {str(e)}")

# Test 3: LlamaParseClient with fallback chain
logger.info("\n\n=== Test 3: LlamaParseClient (with fallbacks) ===")
try:
    from app.services.pdf_parsing.llama_parse_client import LlamaParseClient
    
    # Initialize the client
    client = LlamaParseClient(
        api_key=api_key,
        result_type="markdown",
        use_academic_instruction=True
    )
    
    # Parse the PDF
    logger.info(f"Parsing PDF: {pdf_path}")
    result = client.parse_pdf(pdf_path)
    
    # Check the result
    logger.info(f"Parsing successful, result length: {len(result)} characters")
    logger.info(f"Line count: {result.count(chr(10)) + 1}")
    
    # Save the result
    output_path = output_dir / "integrated_client_output.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    
    logger.info(f"Output saved to {output_path}")
except Exception as e:
    logger.error(f"Error testing integrated client: {str(e)}")

# Generate summary report
logger.info("\n\n=== Generating Summary Report ===")
try:
    # Get file sizes
    files = list(output_dir.glob("*.md"))
    file_sizes = {}
    for file_path in files:
        file_sizes[file_path.name] = file_path.stat().st_size
    
    # Create a summary report
    summary_path = output_dir / "diagnosis_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("LlamaParse Diagnosis Summary\n")
        f.write("==========================\n\n")
        f.write(f"Test PDF: {pdf_path}\n\n")
        f.write("Output File Sizes:\n")
        for name, size in file_sizes.items():
            f.write(f"- {name}: {size} bytes\n")
        
        f.write("\nLine Counts:\n")
        for file_path in files:
            with open(file_path, "r", encoding="utf-8") as content_file:
                content = content_file.read()
                line_count = content.count('\n') + 1
                f.write(f"- {file_path.name}: {line_count} lines\n")
                
                # Check for truncation indicators
                if content.endswith("...") or "content truncated" in content.lower():
                    f.write(f"  WARNING: Possible truncation detected in {file_path.name}\n")
    
    logger.info(f"Summary report saved to {summary_path}")
except Exception as e:
    logger.error(f"Error generating summary: {str(e)}")

logger.info("Diagnosis complete. Please check the llamaparse_diagnosis directory for outputs.")