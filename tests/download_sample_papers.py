"""
Script to download sample academic papers for testing.

This script downloads a set of open access academic papers from various sources
to use for testing the PDF conversion pipeline.
"""
import os
import argparse
import requests
from pathlib import Path
import concurrent.futures

# Define the corpus directory
CORPUS_DIR = Path(__file__).parent / "pdf_corpus"
PAPERS_DIR = CORPUS_DIR / "papers"

# Sample papers (URLs of open-access academic papers)
SAMPLE_PAPERS = {
    "cs": [
        # Computer Science papers
        ("https://arxiv.org/pdf/1706.03762.pdf", "attention_is_all_you_need.pdf"),
        ("https://arxiv.org/pdf/1512.03385.pdf", "deep_residual_learning.pdf"),
    ],
    "bio": [
        # Biology papers
        ("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7745045/pdf/nihpp-2020.09.22.308619v5.pdf", "cell_biology_2020.pdf"),
    ],
    "physics": [
        # Physics papers
        ("https://arxiv.org/pdf/1803.08823.pdf", "physics_survey.pdf"),
    ],
    "economics": [
        # Economics papers
        ("https://arxiv.org/pdf/1905.10307.pdf", "economics_deep_learning.pdf"),
    ],
    "math": [
        # Mathematics papers
        ("https://arxiv.org/pdf/math/0309285.pdf", "geometry_application.pdf"),
    ]
}

def download_paper(url, output_path):
    """Download a paper from URL to output_path."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True, f"Downloaded {output_path.name}"
    except Exception as e:
        return False, f"Error downloading {url}: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Download sample academic papers for testing')
    parser.add_argument('--category', choices=list(SAMPLE_PAPERS.keys()) + ['all'], default='all',
                        help='Category of papers to download (default: all)')
    args = parser.parse_args()
    
    # Create directories if they don't exist
    for category in SAMPLE_PAPERS:
        (PAPERS_DIR / category).mkdir(parents=True, exist_ok=True)
    
    # Determine which categories to download
    categories = [args.category] if args.category != 'all' else SAMPLE_PAPERS.keys()
    
    # Collect all papers to download
    to_download = []
    for category in categories:
        for url, filename in SAMPLE_PAPERS[category]:
            output_path = PAPERS_DIR / category / filename
            if not output_path.exists():
                to_download.append((url, output_path))
    
    if not to_download:
        print("All papers already downloaded!")
        return
    
    print(f"Will download {len(to_download)} papers")
    
    # Download papers in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(download_paper, url, output_path): output_path.name 
                  for url, output_path in to_download}
        
        for future in concurrent.futures.as_completed(futures):
            filename = futures[future]
            success, message = future.result()
            if success:
                print(f"✓ {message}")
            else:
                print(f"✗ {message}")
    
    # Print success message
    print("\nDownload completed!")
    print(f"Papers downloaded to: {PAPERS_DIR}")
    print("\nTo run the conversion test, use:")
    print("python tests/test_pdf_conversion.py")

if __name__ == "__main__":
    main()
