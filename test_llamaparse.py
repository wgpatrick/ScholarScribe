"""
Test script for LlamaParse integration.

This script tests the LlamaParse client against our test corpus and compares
the results with our custom AcademicPaperParser.
"""
import os
import sys
import json
import time
from pathlib import Path
import argparse
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath("."))

# Import our parsers
from app.services.pdf_parsing.llama_parse_client import LlamaParseClient
from app.services.pdf_parsing.academic_parser import AcademicPaperParser

def setup_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    
    # Verify we have the LlamaCloud API key
    api_token = os.environ.get("LLAMA_CLOUD_API_KEY")
    if not api_token:
        logger.error("LLAMA_CLOUD_API_KEY not found in environment variables or .env file")
        logger.error("Please set this token to use LlamaParse")
        return False
    
    return True

def test_llamaparse(pdf_path, output_dir=None):
    """
    Test LlamaParse on a single PDF.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save output
    """
    if not setup_environment():
        return
    
    logger.info(f"Testing LlamaParse on {pdf_path}")
    
    # Set default output directory
    if output_dir is None:
        output_dir = Path(pdf_path).parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
    
    # Create output paths
    base_name = Path(pdf_path).stem
    output_path = output_dir / f"{base_name}_llamaparse.md"
    metrics_path = output_dir / f"{base_name}_llamaparse_metrics.json"
    
    # Initialize the client with academic paper instructions
    client = LlamaParseClient(
        result_type="markdown", 
        use_academic_instruction=True
    )
    
    # Process the PDF
    start_time = time.time()
    try:
        result = client.parse_pdf(pdf_path)
        processing_time = time.time() - start_time
        
        # Save the output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        # Extract metadata
        metadata = client.extract_metadata(result)
        
        # Calculate metrics
        metrics = {
            "filename": Path(pdf_path).name,
            "processing_time_seconds": processing_time,
            "metadata": metadata
        }
        
        # Save metrics
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"LlamaParse processing completed in {processing_time:.2f} seconds")
        logger.info(f"Output saved to: {output_path}")
        logger.info(f"Metrics saved to: {metrics_path}")
        
        return result, metrics
    
    except Exception as e:
        logger.error(f"Error processing with LlamaParse: {str(e)}")
        return None, {"error": str(e)}

def compare_parsers(pdf_path, output_dir=None):
    """
    Compare LlamaParse and AcademicPaperParser on a single PDF.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save output and comparison
    """
    if not setup_environment():
        return
    
    logger.info(f"Comparing parsers on {pdf_path}")
    
    # Set default output directory
    if output_dir is None:
        output_dir = Path(pdf_path).parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
    
    # Create output paths
    base_name = Path(pdf_path).stem
    comparison_path = output_dir / f"{base_name}_comparison.md"
    
    # Run LlamaParse
    llamaparse_result, llamaparse_metrics = test_llamaparse(pdf_path, output_dir)
    
    # Run AcademicPaperParser
    start_time = time.time()
    custom_parser = AcademicPaperParser(pdf_path)
    custom_result = custom_parser.process()
    custom_time = time.time() - start_time
    
    # Save custom parser output
    custom_output_path = output_dir / f"{base_name}_academic.md"
    with open(custom_output_path, "w", encoding="utf-8") as f:
        f.write(custom_result)
    
    # Create comparison document
    with open(comparison_path, "w", encoding="utf-8") as f:
        f.write(f"# Parser Comparison for {base_name}\n\n")
        
        # Processing time comparison
        f.write("## Processing Time\n\n")
        llamaparse_time = llamaparse_metrics.get('processing_time_seconds')
        if isinstance(llamaparse_time, (int, float)):
            f.write(f"- **LlamaParse**: {llamaparse_time:.2f} seconds\n")
        else:
            f.write(f"- **LlamaParse**: {llamaparse_time}\n")
        f.write(f"- **Custom Parser**: {custom_time:.2f} seconds\n\n")
        
        # Metadata comparison
        f.write("## Metadata Extraction\n\n")
        f.write("### LlamaParse Metadata\n\n")
        llamaparse_metadata = llamaparse_metrics.get("metadata", {})
        f.write(f"- **Title**: {llamaparse_metadata.get('title', 'Not extracted')}\n")
        f.write(f"- **Authors**: {', '.join(llamaparse_metadata.get('authors', ['Not extracted']))}\n")
        f.write(f"- **Abstract**: {(llamaparse_metadata.get('abstract', 'Not extracted') or '')[:100]}...\n")
        f.write(f"- **Sections**: {len(llamaparse_metadata.get('sections', []))}\n\n")
        
        f.write("### Custom Parser Metadata\n\n")
        f.write(f"- **Title**: {custom_parser.metadata.get('title', 'Not extracted')}\n")
        f.write(f"- **Authors**: {', '.join(custom_parser.metadata.get('authors', ['Not extracted']))}\n")
        f.write(f"- **Abstract**: {(custom_parser.metadata.get('abstract', 'Not extracted') or '')[:100]}...\n")
        f.write(f"- **Sections**: {len(custom_parser.sections)}\n\n")
        
        # Output comparison (excerpts)
        f.write("## Output Comparison\n\n")
        f.write("### LlamaParse Output (First 20 lines)\n\n")
        f.write("```markdown\n")
        if llamaparse_result:
            f.write("\n".join(llamaparse_result.split("\n")[:20]))
        else:
            f.write("Error: No output generated")
        f.write("\n```\n\n")
        
        f.write("### Custom Parser Output (First 20 lines)\n\n")
        f.write("```markdown\n")
        f.write("\n".join(custom_result.split("\n")[:20]))
        f.write("\n```\n\n")
        
        # Qualitative assessment
        f.write("## Qualitative Assessment\n\n")
        f.write("### Structure Preservation\n\n")
        f.write("- **LlamaParse**: [To be assessed]\n")
        f.write("- **Custom Parser**: [To be assessed]\n\n")
        
        f.write("### Multi-column Handling\n\n")
        f.write("- **LlamaParse**: [To be assessed]\n")
        f.write("- **Custom Parser**: [To be assessed]\n\n")
        
        f.write("### Table and Figure Handling\n\n")
        f.write("- **LlamaParse**: [To be assessed]\n")
        f.write("- **Custom Parser**: [To be assessed]\n\n")
        
        f.write("### Reference Processing\n\n")
        f.write("- **LlamaParse**: [To be assessed]\n")
        f.write("- **Custom Parser**: [To be assessed]\n\n")
    
    logger.info(f"Comparison saved to: {comparison_path}")
    
    return comparison_path

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description="Test LlamaParse integration")
    parser.add_argument("--pdf", help="Path to a specific PDF file to test")
    parser.add_argument("--dir", help="Directory containing PDFs to test")
    parser.add_argument("--output", help="Output directory for results")
    parser.add_argument("--compare", action="store_true", help="Compare with custom parser")
    args = parser.parse_args()
    
    if not args.pdf and not args.dir:
        # Default to using our test corpus
        args.dir = "tests/pdf_corpus/papers"
    
    if args.pdf:
        pdf_path = Path(args.pdf)
        if not pdf_path.exists() or pdf_path.suffix.lower() != '.pdf':
            logger.error(f"Invalid PDF file: {pdf_path}")
            return
        
        if args.compare:
            compare_parsers(str(pdf_path), args.output)
        else:
            test_llamaparse(str(pdf_path), args.output)
    
    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists() or not dir_path.is_dir():
            logger.error(f"Invalid directory: {dir_path}")
            return
        
        # Find all PDFs
        pdfs = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".pdf"):
                    pdfs.append(Path(root) / file)
        
        if not pdfs:
            logger.error(f"No PDF files found in {dir_path}")
            return
        
        logger.info(f"Found {len(pdfs)} PDF files to process")
        
        for pdf_path in pdfs:
            if args.compare:
                compare_parsers(str(pdf_path), args.output)
            else:
                test_llamaparse(str(pdf_path), args.output)

if __name__ == "__main__":
    main()
