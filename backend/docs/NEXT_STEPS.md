# Next Steps for Academic Paper Parser Enhancement

Based on our implementation of the AcademicPaperParser and initial testing with real academic papers, we've identified the following next steps to further enhance the conversion quality.

## 1. Enhanced Structure Detection

### Improved Multi-column Layout Handling
- Implement column detection based on text block positioning
- Use clustering algorithms to group text blocks into columns
- Maintain proper reading order within each column
- Handle mixed layouts (e.g., full-width abstracts with multi-column main text)

Sample approach:
```python
def detect_columns(page_blocks):
    """Detect columns based on x-coordinate clustering."""
    # Cluster blocks based on x-coordinate of center point
    x_centers = [block["bbox"][0] + (block["bbox"][2] - block["bbox"][0])/2 for block in page_blocks]
    clustering = DBSCAN(eps=50, min_samples=5).fit(np.array(x_centers).reshape(-1, 1))
    
    # Group blocks by column
    columns = {}
    for i, label in enumerate(clustering.labels_):
        if label not in columns:
            columns[label] = []
        columns[label].append(page_blocks[i])
    
    # Sort columns from left to right
    sorted_columns = []
    for label in sorted(columns.keys()):
        # Sort blocks within column by y-coordinate (top to bottom)
        columns[label].sort(key=lambda b: b["bbox"][1])
        sorted_columns.append(columns[label])
    
    return sorted_columns
```

### Refined Heading Detection
- Use more advanced heuristics for heading detection:
  - Font size relative to surrounding text
  - Font weight and style (bold, italic)
  - Numbering patterns (e.g., "1. Introduction", "2.3 Methods")
  - Spatial positioning (centered text, indentation)
- Extract and assign proper heading levels

Sample approach:
```python
def detect_heading_level(block, context_blocks):
    """Determine heading level based on multiple features."""
    # Extract features
    font_size = max([span.get("size", 0) for line in block["lines"] for span in line["spans"]])
    is_bold = any(span.get("flags", 0) & 2 > 0 for line in block["lines"] for span in line["spans"])
    is_centered = is_text_centered(block)
    has_numbering = bool(re.match(r"^\d+(\.\d+)*\s", block["text"]))
    
    # Calculate context features
    context_sizes = [max([span.get("size", 0) for line in b["lines"] for span in line["spans"]]) 
                    for b in context_blocks]
    avg_size = sum(context_sizes) / len(context_sizes) if context_sizes else 0
    
    # Apply rules to determine level
    if font_size > avg_size * 1.5 or (is_centered and font_size > avg_size * 1.2):
        return 1  # H1
    elif font_size > avg_size * 1.2 or (is_bold and has_numbering):
        return 2  # H2
    elif font_size > avg_size * 1.1 or is_bold:
        return 3  # H3
    elif has_numbering:
        return 4  # H4
    else:
        return None  # Not a heading
```

## 2. Content-Specific Processing

### Table Detection and Processing
- Identify table structures using:
  - Grid lines detection
  - Cell alignment patterns
  - Caption detection ("Table X:")
- Extract table data into Markdown tables or structured HTML

Sample approach:
```python
def detect_tables(page):
    """Detect tables on a page."""
    # Look for grid lines
    lines = page.get_drawings()
    horizontal_lines = [l for l in lines if abs(l["rect"][1] - l["rect"][3]) < 2]
    vertical_lines = [l for l in lines if abs(l["rect"][0] - l["rect"][2]) < 2]
    
    # Check for grid pattern
    if len(horizontal_lines) > 2 and len(vertical_lines) > 2:
        # Find table boundaries
        table_top = min([l["rect"][1] for l in horizontal_lines])
        table_bottom = max([l["rect"][3] for l in horizontal_lines])
        table_left = min([l["rect"][0] for l in vertical_lines])
        table_right = max([l["rect"][2] for l in vertical_lines])
        
        # Find table caption
        blocks = page.get_text("dict")["blocks"]
        captions = [b for b in blocks if "Table" in b["text"] and ":" in b["text"]]
        
        # Extract cells and content
        # ...
```

### Figure Detection and Referencing
- Detect figures using:
  - Image blocks
  - Figure captions ("Figure X:")
  - Visual elements
- Create Markdown references with placeholders

### Equation Handling
- Detect mathematical equations using:
  - Font type (e.g., Math fonts)
  - Special characters frequency
  - Equation delimiters
- Use LaTeX-compatible formatting or MathJax integration

## 3. LLM Integration for Semantic Enhancement

### OpenAI API Integration
- Set up OpenAI API client with proper error handling and rate limiting
- Create prompt templates for different enhancement tasks
- Implement caching to reduce API calls

Sample approach:
```python
def enhance_with_openai(document_text, section_text, task="classify"):
    """Use OpenAI to enhance document processing."""
    prompts = {
        "classify": f"Classify the following section of an academic paper: {section_text[:500]}...",
        "summarize": f"Summarize the following section in 2-3 sentences: {section_text[:1000]}...",
        "extract_metadata": f"Extract title, authors, and affiliations from: {document_text[:1000]}...",
    }
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an academic paper analysis assistant."},
            {"role": "user", "content": prompts[task]}
        ],
        temperature=0.0,
        max_tokens=200
    )
    
    return response.choices[0].message.content
```

### Post-processing Improvements
- Use LLM to:
  - Improve section classification
  - Enhance metadata extraction
  - Generate missing titles or headings
  - Structure references properly
  - Identify key terms and concepts

## 4. Implementation Timeline

1. **Week 1: Enhanced Structure Detection**
   - Implement multi-column detection (2 days)
   - Improve heading detection (2 days)
   - Refine paragraph boundaries (1 day)

2. **Week 2: Content-Specific Processing**
   - Implement table detection (2 days)
   - Add figure handling (1 day)
   - Develop equation detection (2 days)

3. **Week 3: LLM Integration**
   - Set up OpenAI integration (1 day)
   - Implement semantic enhancement (2 days)
   - Create metadata extraction improvements (1 day)
   - Testing and refinement (1 day)

4. **Week 4: Quality Assurance**
   - Comprehensive testing with diverse papers (2 days)
   - Performance optimization (1 day)
   - Documentation and examples (1 day)
   - Integration with main application (1 day)
