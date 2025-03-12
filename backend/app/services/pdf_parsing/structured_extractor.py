"""
Structured Data Extractor

This module extracts structured data from parsed academic papers.
"""
import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class StructuredPaperExtractor:
    """
    Extracts structured data from markdown representation of academic papers.
    """
    
    def __init__(self, markdown_content: str):
        """
        Initialize the extractor with markdown content.
        
        Args:
            markdown_content: The markdown representation of an academic paper
        """
        self.markdown = markdown_content
        self.lines = markdown_content.split('\n')
        self.structured_data = {
            "title": None,
            "authors": [],
            "abstract": None,
            "keywords": [],
            "sections": [],
            "references": [],
            "figures": [],
            "tables": [],
            "equations": []
        }
    
    def extract(self) -> Dict[str, Any]:
        """
        Extract all structured data from the markdown content.
        
        Returns:
            Dict: Structured data containing title, authors, abstract, sections, etc.
        """
        self._extract_title()
        self._extract_authors()
        self._extract_abstract()
        self._extract_sections()
        self._extract_references()
        self._extract_figures_and_tables()
        self._extract_keywords()
        
        return self.structured_data
    
    def _extract_title(self) -> None:
        """Extract the paper title (usually the first heading)."""
        for line in self.lines:
            if line.startswith('# '):
                self.structured_data["title"] = line[2:].strip()
                break
                
        # If no title found with #, look for the first non-empty line
        if not self.structured_data["title"]:
            for line in self.lines:
                if line.strip() and not line.startswith('#') and not line.startswith('---'):
                    self.structured_data["title"] = line.strip()
                    break
    
    def _extract_authors(self) -> None:
        """Extract the paper authors."""
        # Look for lines with author patterns
        author_section_started = False
        authors = []
        
        # First check for explicitly marked authors section or list
        for i, line in enumerate(self.lines):
            if "author" in line.lower() and ":" in line:
                # Pattern like "**Authors:** Author1, Author2"
                parts = line.split(":", 1)
                if len(parts) > 1:
                    # Split by comma or and
                    author_text = parts[1].strip()
                    authors.extend([a.strip() for a in re.split(r',|\band\b', author_text) if a.strip()])
                break
            elif line.startswith('- ') and ('author' in self.lines[i-1].lower() or author_section_started):
                # Pattern with bullet points for authors
                author_section_started = True
                authors.append(line[2:].strip())
            elif author_section_started and not line.startswith('- ') and line.strip():
                # End of author section
                author_section_started = False
        
        # If no authors found with explicit markers, try different pattern recognition
        if not authors:
            # Look for email addresses or affiliations to identify author lines
            for i, line in enumerate(self.lines[:20]):  # Check first 20 lines
                if '@' in line and not line.startswith('#'):
                    # Possible author line with email
                    authors.append(line.strip())
                elif re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', line) and i < 10:
                    # Names in Title Case in first 10 lines
                    authors.append(line.strip())
        
        self.structured_data["authors"] = authors
    
    def _extract_abstract(self) -> None:
        """Extract the paper abstract."""
        abstract_lines = []
        in_abstract = False
        
        # Look for abstract section heading
        for i, line in enumerate(self.lines):
            if re.match(r'^#+\s+Abstract\b', line, re.IGNORECASE) or re.match(r'^Abstract\b', line, re.IGNORECASE):
                in_abstract = True
                continue
            elif in_abstract and line.startswith('#'):
                # End of abstract section
                in_abstract = False
                break
            elif in_abstract and line.strip():
                abstract_lines.append(line.strip())
        
        # If not found by section heading, try looking for an "Abstract:" line
        if not abstract_lines:
            for i, line in enumerate(self.lines):
                if line.lower().startswith('abstract:') or line.lower().startswith('**abstract:**'):
                    # Extract text after "Abstract:"
                    if ':' in line:
                        abstract_part = line.split(':', 1)[1].strip()
                        if abstract_part:
                            abstract_lines.append(abstract_part)
                    
                    # Collect lines until next heading or empty line
                    j = i + 1
                    while j < len(self.lines) and not self.lines[j].startswith('#') and self.lines[j].strip():
                        abstract_lines.append(self.lines[j].strip())
                        j += 1
                    break
        
        # Join abstract lines into a single text
        if abstract_lines:
            self.structured_data["abstract"] = ' '.join(abstract_lines)
    
    def _extract_sections(self) -> None:
        """Extract the paper sections with their content."""
        sections = []
        current_section = None
        current_content = []
        
        for line in self.lines:
            if line.startswith('#'):
                # Save previous section if exists
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_content),
                        "level": self._get_heading_level(current_section)
                    })
                    current_content = []
                
                # Start new section
                heading_level = 0
                for char in line:
                    if char == '#':
                        heading_level += 1
                    else:
                        break
                
                current_section = line[heading_level:].strip()
            elif current_section and line.strip():
                current_content.append(line)
        
        # Add the last section
        if current_section:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content),
                "level": self._get_heading_level(current_section)
            })
        
        self.structured_data["sections"] = sections
    
    def _get_heading_level(self, heading_text: str) -> int:
        """
        Determine the heading level from the original markdown.
        
        Args:
            heading_text: The text of the heading (without # markers)
            
        Returns:
            int: The heading level (1-6)
        """
        for i, line in enumerate(self.lines):
            if line.startswith('#') and heading_text in line:
                level = 0
                for char in line:
                    if char == '#':
                        level += 1
                    else:
                        break
                return level
        return 1  # Default to level 1 if not found
    
    def _extract_references(self) -> None:
        """Extract the paper references."""
        references = []
        in_references = False
        
        # Look for references section
        for line in self.lines:
            if re.match(r'^#+\s+References\b', line, re.IGNORECASE) or re.match(r'^References\b', line, re.IGNORECASE):
                in_references = True
                continue
            elif in_references and line.startswith('#'):
                # End of references section
                in_references = False
                break
            elif in_references and line.strip():
                # Check if it's a numbered reference
                if re.match(r'^\d+\.?\s+', line) or re.match(r'^\[\d+\]\s+', line):
                    references.append(line.strip())
                elif references and line.strip():
                    # Continuation of previous reference
                    references[-1] += ' ' + line.strip()
        
        self.structured_data["references"] = references
    
    def _extract_figures_and_tables(self) -> None:
        """Extract figures and tables mentioned in the text."""
        figures = []
        tables = []
        
        # Look for Markdown-style image links
        figure_pattern = r'!\[(.*?)\]\((.*?)\)'
        for match in re.finditer(figure_pattern, self.markdown):
            alt_text = match.group(1)
            url = match.group(2)
            figures.append({
                "caption": alt_text,
                "url": url
            })
        
        # Look for figure captions in text
        for i, line in enumerate(self.lines):
            if 'figure' in line.lower() and ':' in line:
                caption = line.split(':', 1)[1].strip()
                if caption:
                    figures.append({
                        "caption": caption,
                        "url": None
                    })
        
        # Look for tables (usually denoted by | characters for table borders)
        in_table = False
        current_table = []
        table_caption = None
        
        for line in self.lines:
            if 'table' in line.lower() and ':' in line:
                # Table caption
                table_caption = line.split(':', 1)[1].strip()
                in_table = True
                current_table = []
            elif in_table:
                if '|' in line:
                    # Table row
                    current_table.append(line.strip())
                elif line.strip() == '' and current_table:
                    # End of table
                    tables.append({
                        "caption": table_caption,
                        "content": '\n'.join(current_table)
                    })
                    in_table = False
                    current_table = []
                    table_caption = None
        
        # Add last table if exists
        if in_table and current_table:
            tables.append({
                "caption": table_caption,
                "content": '\n'.join(current_table)
            })
        
        self.structured_data["figures"] = figures
        self.structured_data["tables"] = tables
    
    def _extract_keywords(self) -> None:
        """Extract keywords if mentioned in the document."""
        keywords = []
        
        # Look for a keywords section
        for i, line in enumerate(self.lines):
            if 'keywords' in line.lower() and ':' in line:
                # Extract keywords after the colon
                keyword_text = line.split(':', 1)[1].strip()
                # Split by common separators
                keywords.extend([k.strip() for k in re.split(r',|;', keyword_text) if k.strip()])
                break
        
        self.structured_data["keywords"] = keywords


def extract_structured_data(markdown: str) -> Dict[str, Any]:
    """
    Extract structured data from markdown text of an academic paper.
    
    Args:
        markdown: The markdown text of the academic paper
        
    Returns:
        Dict: Structured data containing title, authors, abstract, sections, etc.
    """
    extractor = StructuredPaperExtractor(markdown)
    return extractor.extract()


def extract_field(markdown: str, field: str) -> Any:
    """
    Extract a specific field from the markdown text.
    
    Args:
        markdown: The markdown text of the academic paper
        field: The field to extract (title, abstract, authors, etc.)
        
    Returns:
        Any: The extracted field value
    """
    structured_data = extract_structured_data(markdown)
    return structured_data.get(field)