"""
Visualization tool for PDF conversion results.

This script provides a side-by-side comparison of the original PDF 
and the converted markdown.
"""
import sys
import os
import argparse
from pathlib import Path

# Check if we're running in a terminal environment
IS_TERMINAL = sys.stdout.isatty()

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m' if IS_TERMINAL else ''
    BLUE = '\033[94m' if IS_TERMINAL else ''
    GREEN = '\033[92m' if IS_TERMINAL else ''
    WARNING = '\033[93m' if IS_TERMINAL else ''
    FAIL = '\033[91m' if IS_TERMINAL else ''
    ENDC = '\033[0m' if IS_TERMINAL else ''
    BOLD = '\033[1m' if IS_TERMINAL else ''
    UNDERLINE = '\033[4m' if IS_TERMINAL else ''

def main():
    parser = argparse.ArgumentParser(description='Visualize PDF conversion results')
    parser.add_argument('filename', help='PDF filename (without extension) to visualize')
    args = parser.parse_args()
    
    # Define paths
    corpus_dir = Path(__file__).parent / "pdf_corpus"
    
    # Search for the PDF file in the papers directory recursively
    pdf_path = None
    for root, _, files in os.walk(corpus_dir / "papers"):
        for file in files:
            if file.startswith(args.filename) and file.endswith(".pdf"):
                pdf_path = Path(root) / file
                break
    
    if not pdf_path:
        print(f"{Colors.FAIL}PDF file not found: {args.filename}{Colors.ENDC}")
        return
    
    # Find the corresponding markdown file
    md_path = corpus_dir / "outputs" / f"{args.filename}.md"
    if not md_path.exists():
        print(f"{Colors.FAIL}Markdown output not found: {md_path}{Colors.ENDC}")
        return
    
    # Find the metrics file
    metrics_path = corpus_dir / "metrics" / f"{args.filename}_metrics.json"
    if metrics_path.exists():
        import json
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        
        print(f"\n{Colors.BOLD}{Colors.HEADER}=== Conversion Metrics ==={Colors.ENDC}")
        print(f"{Colors.BOLD}File:{Colors.ENDC} {metrics.get('filename', 'Unknown')}")
        print(f"{Colors.BOLD}Processing Time:{Colors.ENDC} {metrics.get('processing_time_seconds', 0):.2f} seconds")
        print(f"{Colors.BOLD}Word Count:{Colors.ENDC} {metrics.get('word_count', 0)}")
        print(f"{Colors.BOLD}Line Count:{Colors.ENDC} {metrics.get('line_count', 0)}")
        print(f"{Colors.BOLD}Heading Count:{Colors.ENDC} {metrics.get('heading_count', 0)}")
        print(f"{Colors.BOLD}Status:{Colors.ENDC} {metrics.get('status', 'Unknown')}")
    
    # Read the markdown content
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # Display the results
    print(f"\n{Colors.BOLD}{Colors.HEADER}=== PDF Path ==={Colors.ENDC}")
    print(f"{pdf_path}")
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}=== Markdown Output ==={Colors.ENDC}")
    print(f"{Colors.GREEN}{md_content[:2000]}{Colors.ENDC}")
    if len(md_content) > 2000:
        print(f"{Colors.WARNING}... (truncated, showing first 2000 characters){Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}=== Next Steps ==={Colors.ENDC}")
    print("1. Examine the output markdown for accuracy")
    print("2. Check if headings are correctly identified")
    print("3. Verify that document structure is preserved")
    print("4. Look for any missing content or formatting issues")

if __name__ == "__main__":
    main()
