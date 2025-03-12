# Academic Paper Parsing Services - Detailed Research

## LlamaParse

### Access Options

1. **API Access via AnthropicPro**
   - Offers LlamaParse as a document processing API
   - Pricing: Pay-per-use model, typically $0.005-0.01 per page
   - Documentation: Available through AnthropicPro developer portal
   - Authentication: API key based

2. **Replicate.com Integration**
   - Hosts LlamaParse models
   - API endpoint: https://replicate.com/replicate/llama-parse
   - Pricing: Pay-per-run, approximately $0.01 per page
   - Easy REST API integration

3. **Hugging Face Inference API**
   - May offer LlamaParse through their inference API
   - Pricing: Token-based pricing structure
   - Implementation: Simple REST API

### Sample Implementation (Replicate)

```python
import replicate
import os

def parse_pdf_with_llamaparse(pdf_path):
    """Parse PDF with LlamaParse via Replicate."""
    
    # Set API token
    os.environ["REPLICATE_API_TOKEN"] = "YOUR_REPLICATE_API_TOKEN"
    
    # Read PDF file as bytes
    with open(pdf_path, "rb") as file:
        pdf_bytes = file.read()
    
    # Run LlamaParse
    output = replicate.run(
        "replicate/llama-parse:73ee089d5a5110abfa5eaae555dc541be3f369e5c878b12656be87b306286dbe",
        input={
            "file": pdf_bytes,
            "output_format": "markdown",
            "processing_type": "academic_paper"
        }
    )
    
    return output
```

## Unstructured.io

### Access Options

1. **Direct Python Package**
   - `pip install unstructured`
   - Open-source, self-hosted option
   - No API costs, but requires more implementation work
   - Documentation: https://unstructured-io.github.io/unstructured/

2. **Unstructured API (Hosted Service)**
   - REST API for document processing
   - Pricing: Free tier available, then pay-per-document
   - Enterprise plans for higher volume

### Sample Implementation (Direct Package)

```python
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.strategies import select_strategy
from unstructured.staging.md import stage_for_markdown

def parse_pdf_with_unstructured(pdf_path):
    """Parse PDF with Unstructured.io library."""
    
    # Configure strategy optimized for academic papers
    strategy = select_strategy(
        strategy_name="scientific_article",
        page_number_extraction=True,
        table_extraction=True,
        infer_heading_levels=True
    )
    
    # Partition the PDF
    elements = partition_pdf(
        filename=pdf_path,
        strategy=strategy,
        extract_images=True
    )
    
    # Convert to Markdown
    markdown = stage_for_markdown(elements)
    
    return markdown
```

## SciSpace (Formerly Typeset)

### Access Options

1. **SciSpace Parser API**
   - Specialized in scientific and academic paper processing
   - Pricing: Free tier (limited docs per month), then pay-per-document
   - Documentation: https://typeset.io/api-documentation
   - Features: Structured JSON output with sections, references, tables, etc.

### Sample Implementation

```python
import requests
import json

def parse_pdf_with_scispace(pdf_path, api_key):
    """Parse PDF with SciSpace Parser API."""
    
    # Prepare API request
    url = "https://api.scispace.com/v1/pdf/extract"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "multipart/form-data"
    }
    
    # Upload file
    with open(pdf_path, "rb") as file:
        files = {"file": file}
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        result = response.json()
        
        # Convert to Markdown format
        markdown = convert_scispace_to_markdown(result)
        return markdown
    else:
        raise Exception(f"SciSpace API error: {response.text}")
```

## Grobid + Citation.js

### Access Options

1. **Self-hosted Open Source Solution**
   - Grobid: Extracts structured data from academic papers
   - Citation.js: Handles citations and references
   - No API costs, but requires server setup
   - Documentation: https://grobid.readthedocs.io/

### Sample Implementation

```python
import requests
import xml.etree.ElementTree as ET
import subprocess
import os

def parse_pdf_with_grobid(pdf_path, grobid_url="http://localhost:8070"):
    """Parse PDF with self-hosted Grobid."""
    
    # Upload to Grobid for processing
    with open(pdf_path, "rb") as file:
        files = {"input": file}
        response = requests.post(
            f"{grobid_url}/api/processFulltextDocument",
            files=files
        )
    
    if response.status_code == 200:
        # Parse TEI XML response
        tei_xml = response.text
        
        # Convert TEI XML to Markdown (simplified example)
        markdown = convert_tei_to_markdown(tei_xml)
        return markdown
    else:
        raise Exception(f"Grobid error: {response.status_code}")
```

## Cost Comparison

| Service | Free Tier | Pay-as-you-go | Enterprise |
|---------|-----------|---------------|------------|
| LlamaParse via Replicate | No | ~$0.01/page | Custom |
| Unstructured.io (hosted) | 100 docs/month | $0.04-0.10/doc | Custom |
| SciSpace | 25 docs/month | $0.10-0.20/doc | From $199/month |
| Grobid (self-hosted) | Unlimited | Server costs only | Server costs only |

## Feature Comparison

| Feature | LlamaParse | Unstructured.io | SciSpace | Grobid |
|---------|------------|-----------------|----------|--------|
| Multi-column handling | Excellent | Good | Excellent | Good |
| Table extraction | Excellent | Good | Excellent | Limited |
| Figure handling | Good | Basic | Good | Limited |
| Math equation support | Excellent | Limited | Good | Limited |
| Reference linking | Yes | Basic | Yes | Yes |
| Metadata extraction | Yes | Yes | Yes | Yes |
| Output formats | MD, JSON, HTML | MD, JSON | JSON | XML, JSON |
| Academic focus | High | Medium | High | High |

## Recommendations

Based on the research, here are recommended options in order of preference:

1. **LlamaParse via Replicate**
   - Best overall quality for academic papers
   - Reasonable per-page pricing
   - Simple API integration
   - Excellent handling of all academic paper elements

2. **Unstructured.io (Direct Package)**
   - Good quality for general document parsing
   - Free and open-source
   - Requires more custom development but no ongoing API costs
   - May need enhancements for academic paper specifics

3. **SciSpace**
   - Specialized in academic papers
   - Good free tier for initial development
   - More expensive than alternatives at scale
   - Excellent metadata extraction

4. **Grobid (Self-hosted)**
   - Research-focused parser with excellent bibliography handling
   - Requires server setup and maintenance
   - Most complex integration but no API costs
   - Strong scholarly document model

## Implementation Strategy

For our application, the recommended implementation strategy is:

1. **Start with LlamaParse** via Replicate for the best out-of-the-box academic paper parsing
2. **Implement error handling** and fallbacks
3. **Set up caching** to reduce API costs for frequently accessed documents
4. **Evaluate real-world performance** with diverse papers from different fields

### Code Example for Recommended Approach

```python
import os
import replicate
import requests
import tempfile
from functools import lru_cache

class AcademicPaperParser:
    """Parse academic papers using LlamaParse with fallbacks."""
    
    def __init__(self, replicate_api_key):
        self.replicate_api_key = replicate_api_key
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_key
    
    @lru_cache(maxsize=100)  # Cache results to reduce API calls
    def parse_pdf(self, pdf_path):
        """
        Parse PDF file to Markdown with LlamaParse.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            str: Structured Markdown representation of the paper
        """
        try:
            # First try with LlamaParse
            return self._parse_with_llamaparse(pdf_path)
        except Exception as e:
            print(f"LlamaParse failed: {str(e)}")
            try:
                # Fallback to Unstructured
                return self._parse_with_unstructured(pdf_path)
            except Exception as e2:
                print(f"Unstructured fallback failed: {str(e2)}")
                # Last resort: basic PyMuPDF extraction
                return self._basic_pdf_extraction(pdf_path)
    
    def _parse_with_llamaparse(self, pdf_path):
        """Parse with LlamaParse via Replicate."""
        with open(pdf_path, "rb") as file:
            pdf_bytes = file.read()
        
        output = replicate.run(
            "replicate/llama-parse:73ee089d5a5110abfa5eaae555dc541be3f369e5c878b12656be87b306286dbe",
            input={
                "file": pdf_bytes,
                "output_format": "markdown",
                "processing_type": "academic_paper"
            }
        )
        
        return output
        
    def _parse_with_unstructured(self, pdf_path):
        """Parse with Unstructured.io as fallback."""
        # Implementation would use unstructured package if installed
        # This is a placeholder - would need to install package
        raise NotImplementedError("Unstructured fallback not implemented")
    
    def _basic_pdf_extraction(self, pdf_path):
        """Basic extraction using PyMuPDF as last resort."""
        import fitz  # PyMuPDF
        
        doc = fitz.open(pdf_path)
        text = []
        
        # Extract title from first page if possible
        if len(doc) > 0:
            title = os.path.basename(pdf_path).replace(".pdf", "")
            text.append(f"# {title}\n\n")
        
        # Extract text from each page
        for page in doc:
            text.append(page.get_text())
        
        doc.close()
        return "\n".join(text)
```
