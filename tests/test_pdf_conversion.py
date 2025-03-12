"""Test script for PDF conversion evaluation.

This script processes a corpus of academic PDFs and evaluates the conversion quality.
"""
import os
import json
import time
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import from the app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.pdf_converter import PDFConverterService
from app.models.document import Document

# Define paths
CORPUS_DIR = Path(__file__).parent / "pdf_corpus"
PAPERS_DIR = CORPUS_DIR / "papers"
OUTPUTS_DIR = CORPUS_DIR / "outputs"
METRICS_DIR = CORPUS_DIR / "metrics"

# Ensure output directories exist
OUTPUTS_DIR.mkdir(exist_ok=True)
METRICS_DIR.mkdir(exist_ok=True)

class MockDocument:
    """Mock document class for testing conversion without database."""
    
    def __init__(self, pdf_path):
        self.id = Path(pdf_path).stem
        self.pdf_path = str(pdf_path)
        self.markdown_text = None
        self.conversion_status = "pending"

class MockDB:
    """Mock database session for testing."""
    
    def __init__(self):
        self.docs = {}
    
    def commit(self):
        """Mock commit method."""
        pass
    
    def query(self, model):
        """Mock query method that returns a MockQuery."""
        return MockQuery(self.docs)

class MockQuery:
    """Mock query class for testing."""
    
    def __init__(self, docs):
        self.docs = docs
    
    def filter(self, condition):
        """Mock filter method that returns self."""
        return self
    
    def first(self):
        """Mock first method that returns the first document."""
        if self.docs:
            return list(self.docs.values())[0]
        return None

async def process_pdf(pdf_path):
    """Process a single PDF and return metrics."""
    start_time = time.time()
    
    # Create a mock document
    doc = MockDocument(pdf_path)
    mock_db = MockDB()
    mock_db.docs[doc.id] = doc
    
    # Run the conversion
    converter = PDFConverterService()
    await converter.convert_pdf_to_markdown(doc.id, mock_db)
    
    # Calculate processing time
    processing_time = time.time() - start_time
    
    # Get the output
    markdown_text = doc.markdown_text or "No content generated"
    
    # Save the output to a file
    output_path = OUTPUTS_DIR / f"{Path(pdf_path).stem}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)
    
    # Calculate basic metrics
    word_count = len(markdown_text.split())
    line_count = len(markdown_text.splitlines())
    heading_count = markdown_text.count("\n#")
    
    # Create a metrics object
    metrics = {
        "filename": Path(pdf_path).name,
        "processing_time_seconds": processing_time,
        "word_count": word_count,
        "line_count": line_count,
        "heading_count": heading_count,
        "status": doc.conversion_status,
        "timestamp": datetime.now().isoformat()
    }
    
    # Save metrics to a file
    metrics_path = METRICS_DIR / f"{Path(pdf_path).stem}_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    
    return metrics

async def process_corpus():
    """Process all PDFs in the corpus."""
    # Find all PDFs in the corpus
    pdfs = []
    for root, _, files in os.walk(PAPERS_DIR):
        for file in files:
            if file.endswith(".pdf"):
                pdfs.append(Path(root) / file)
    
    if not pdfs:
        print("No PDFs found in the corpus directory!")
        return
    
    print(f"Found {len(pdfs)} PDFs to process")
    
    # Process each PDF
    all_metrics = []
    for pdf_path in pdfs:
        print(f"Processing {pdf_path.name}...")
        metrics = await process_pdf(pdf_path)
        all_metrics.append(metrics)
        print(f"  Completed in {metrics['processing_time_seconds']:.2f} seconds")
    
    # Save overall metrics summary
    summary_path = METRICS_DIR / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)
    
    # Print summary
    print("\nConversion Summary:")
    print(f"Total PDFs processed: {len(all_metrics)}")
    total_time = sum(m["processing_time_seconds"] for m in all_metrics)
    print(f"Total processing time: {total_time:.2f} seconds")
    print(f"Average processing time: {total_time/len(all_metrics):.2f} seconds per PDF")
    print(f"Outputs saved to: {OUTPUTS_DIR}")
    print(f"Metrics saved to: {METRICS_DIR}")

if __name__ == "__main__":
    asyncio.run(process_corpus())
