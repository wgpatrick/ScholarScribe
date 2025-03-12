"""
Test script for structured data extraction from academic papers.
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

# Import our parser
from app.services.pdf_parsing.llama_parse_client import LlamaParseClient

def main():
    """Test structured data extraction from PDFs."""
    # Check for API key
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    if not api_key:
        logger.error("LLAMA_CLOUD_API_KEY not found in environment variables")
        sys.exit(1)
    
    # Find all PDF files in the test corpus
    all_test_papers = []
    for root, dirs, files in os.walk("tests/pdf_corpus/papers"):
        for file in files:
            if file.endswith(".pdf"):
                all_test_papers.append(os.path.join(root, file))
    
    logger.info(f"Found {len(all_test_papers)} test papers in corpus")
    
    # Limit to 3 papers for now to avoid processing too many
    test_papers = all_test_papers[:3]
    logger.info(f"Testing with papers: {test_papers}")
    
    # Create output directory
    output_dir = Path("structured_extraction_results")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize the LlamaParseClient
    client = LlamaParseClient(
        api_key=api_key,
        result_type="markdown",
        use_academic_instruction=True
    )
    
    # Process each test paper
    for pdf_path in test_papers:
        if not os.path.exists(pdf_path):
            logger.warning(f"File not found: {pdf_path}")
            continue
            
        logger.info(f"Processing: {pdf_path}")
        
        try:
            # Parse with structured data extraction
            content, structured_data = client.parse_pdf(pdf_path, return_structured=True)
            
            # Get base name for output files
            base_name = Path(pdf_path).stem
            
            # Save the markdown content
            markdown_path = output_dir / f"{base_name}_content.md"
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            # Save the structured data as JSON
            json_path = output_dir / f"{base_name}_structured.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(structured_data, f, indent=2)
                
            # Generate a summary file
            summary_path = output_dir / f"{base_name}_summary.md"
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(f"# Summary of {base_name}\n\n")
                
                # Title
                f.write(f"## Title\n{structured_data.get('title', 'Not found')}\n\n")
                
                # Authors
                f.write("## Authors\n")
                for author in structured_data.get('authors', []):
                    f.write(f"- {author}\n")
                f.write("\n")
                
                # Abstract
                f.write("## Abstract\n")
                f.write(f"{structured_data.get('abstract', 'Not found')}\n\n")
                
                # Keywords
                if structured_data.get('keywords'):
                    f.write("## Keywords\n")
                    for keyword in structured_data.get('keywords', []):
                        f.write(f"- {keyword}\n")
                    f.write("\n")
                
                # Sections
                f.write("## Sections\n")
                for section in structured_data.get('sections', []):
                    f.write(f"- {section.get('title')} (Level {section.get('level')})\n")
                f.write("\n")
                
                # References count
                f.write(f"## References\n{len(structured_data.get('references', []))} references found\n\n")
                
            logger.info(f"Results saved to {output_dir}")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")

if __name__ == "__main__":
    main()