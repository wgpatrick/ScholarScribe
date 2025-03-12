"""
Script to test the AcademicPaperParser with papers from our test corpus.
"""
import sys
import os
import json
from pathlib import Path
import time
import argparse

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.services.pdf_parsing.academic_parser import AcademicPaperParser

def test_parser(pdf_path, output_dir=None):
    """
    Test the AcademicPaperParser on a single PDF.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save output (defaults to same as PDF)
    """
    print(f"Processing: {pdf_path}")
    
    # Set default output directory
    if output_dir is None:
        output_dir = Path(pdf_path).parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
    
    # Create output paths
    base_name = Path(pdf_path).stem
    markdown_path = output_dir / f"{base_name}_academic.md"
    metrics_path = output_dir / f"{base_name}_academic_metrics.json"
    
    # Process the PDF
    start_time = time.time()
    parser = AcademicPaperParser(pdf_path)
    markdown = parser.process()
    processing_time = time.time() - start_time
    
    # Save the Markdown output
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    # Calculate metrics
    metrics = {
        "filename": Path(pdf_path).name,
        "processing_time_seconds": processing_time,
        "pages": parser.stats["pages"],
        "text_blocks": parser.stats["text_blocks"],
        "images": parser.stats["images"],
        "metadata": {
            "title": parser.metadata.get("title"),
            "authors": parser.metadata.get("authors"),
            "abstract_length": len(parser.metadata.get("abstract", "")) if parser.metadata.get("abstract") else 0,
        },
        "sections": len(parser.sections),
        "references": len(parser.references),
    }
    
    # Save metrics
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Processing completed in {processing_time:.2f} seconds")
    print(f"Markdown saved to: {markdown_path}")
    print(f"Metrics saved to: {metrics_path}")
    
    return metrics

def main():
    parser = argparse.ArgumentParser(description="Test the AcademicPaperParser")
    parser.add_argument("pdf_path", help="Path to PDF file or directory of PDFs")
    parser.add_argument("--output", "-o", help="Output directory for markdown files")
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_path)
    
    if pdf_path.is_file() and pdf_path.suffix.lower() == ".pdf":
        # Process a single PDF
        test_parser(str(pdf_path), args.output)
    
    elif pdf_path.is_dir():
        # Process all PDFs in the directory
        all_metrics = []
        
        # Find all PDFs in the directory (recursively)
        for root, _, files in os.walk(pdf_path):
            for file in files:
                if file.endswith(".pdf"):
                    file_path = Path(root) / file
                    metrics = test_parser(str(file_path), args.output)
                    all_metrics.append(metrics)
        
        # Save summary metrics
        if args.output:
            output_dir = Path(args.output)
        else:
            output_dir = pdf_path
        
        summary_path = output_dir / "summary_academic_parser.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(all_metrics, f, indent=2)
        
        print(f"\nProcessed {len(all_metrics)} PDFs")
        print(f"Summary metrics saved to: {summary_path}")
    
    else:
        print(f"Error: {pdf_path} is not a valid PDF file or directory")

if __name__ == "__main__":
    main()
