# LlamaParse Integration

This document outlines the LlamaParse integration in the Journal Notebook application.

## Overview

LlamaParse is used to convert academic PDF papers into structured text for better readability and analysis. The integration includes the following components:

- `LlamaParseClient`: Main client that orchestrates the parsing process
- `DirectLlamaClient`: Direct implementation of the LlamaCloud API for PDF parsing
- `StructuredPaperExtractor`: Extracts structured data (title, authors, abstract, etc.) from parsed content
- Fallback methods for when LlamaParse is unavailable

## Usage

### Basic Usage

```python
from app.services.pdf_parsing.llama_parse_client import LlamaParseClient

# Initialize the client
client = LlamaParseClient(
    api_key="your_api_key",  # Optional, will use LLAMA_CLOUD_API_KEY env var if not provided
    result_type="markdown",  # Output format (markdown, json, or text)
    use_academic_instruction=True  # Use enhanced instructions for academic papers
)

# Parse a PDF
result = client.parse_pdf("path/to/paper.pdf")
```

### Structured Data Extraction

You can optionally extract structured data from the parsed content:

```python
# Parse a PDF and get structured data
content, structured_data = client.parse_pdf(
    "path/to/paper.pdf", 
    return_structured=True
)

# Now you can access specific parts of the paper
title = structured_data["title"]
abstract = structured_data["abstract"]
authors = structured_data["authors"]
sections = structured_data["sections"]
```

The structured data contains:
- Title
- Authors
- Abstract
- Keywords
- Sections (with title, content, and heading level)
- References
- Figures (if any)
- Tables (if any)

## Implementation Details

Our implementation uses the following strategy to ensure reliable parsing:

1. **Primary Method**: `DirectLlamaClient` - A custom implementation of the LlamaCloud API that communicates directly with the service and provides complete document extraction.

2. **Fallback 1**: Official `LlamaParse` package - If DirectLlamaClient fails, we try the official package. Note that the official package may produce truncated results for some papers.

3. **Fallback 2**: `AcademicPaperParser` - A local parser using PyMuPDF for when API access is unavailable.

4. **Fallback 3**: Basic text extraction - Simple text extraction for when all else fails.

### Important Note on Content Truncation

During testing, we discovered that the official `LlamaParse` package sometimes returns truncated content for academic papers (2-3KB vs 14-15KB with direct API access). 

For this reason, our implementation prioritizes the `DirectLlamaClient` which consistently produces complete results.

## DirectLlamaClient Workflow

The `DirectLlamaClient` implements a three-step workflow to parse PDFs:

1. **Upload** - POST the PDF to `/api/parsing/upload` to start a job
2. **Poll** - Check job status at `/api/parsing/job/{job_id}` until complete
3. **Retrieve** - Get results from `/api/parsing/job/{job_id}/result/{format}`

This approach ensures we get the full document text rather than a truncated version.

## Configuration

The integration requires an API key from LlamaCloud, which can be set in two ways:

1. Pass directly to the `LlamaParseClient` constructor:
```python
client = LlamaParseClient(api_key="your_api_key")
```

2. Set as an environment variable:
```
LLAMA_CLOUD_API_KEY=your_api_key
```

## Troubleshooting

### Full Content Not Extracted

If document content appears truncated:

1. Ensure `DirectLlamaClient` is being used rather than the official package
2. Check the logs for "Using DirectLlamaClient" message
3. Look for content length in the logs (should be 10KB+ for typical papers)

### Connection Issues

If the system can't connect to LlamaCloud API:

1. Check that the API key is correctly set
2. Ensure the host has internet connectivity
3. Verify that api.cloud.llamaindex.ai is accessible from your environment

## Contact

For issues with this implementation, please contact the development team.