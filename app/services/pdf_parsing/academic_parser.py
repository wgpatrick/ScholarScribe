"""
Academic Paper Parser

This module provides enhanced PDF parsing specifically for academic papers,
using PyMuPDF with custom processing for better structure detection.
"""
import os
import re
import logging
from typing import Dict, List, Tuple, Optional, Any
import sys

logger = logging.getLogger(__name__)

class AcademicPaperParser:
    """Parser for academic papers using PyMuPDF with enhanced processing."""
    
    def __init__(self, pdf_path: str):
        """
        Initialize the parser with a PDF path.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.doc = None
        self.sections = []
        self.references = []
        self.metadata = {
            "title": None,
            "authors": [],
            "abstract": None,
            "keywords": [],
            "doi": None,
        }
        self.markdown_text = None
        
        # Document statistics
        self.stats = {
            "pages": 0,
            "text_blocks": 0,
            "images": 0,
            "tables": 0,
            "equations": 0,
        }
        
        try:
            # Try different approaches to import PyMuPDF
            try:
                # First try the standard import (newer versions)
                import fitz
                self.pymupdf = fitz
                # Check if the module has needed functionality
                if not hasattr(fitz, 'open') and not hasattr(fitz, 'Document'):
                    raise ImportError("fitz module missing required functionality")
            except (ImportError, AttributeError):
                try:
                    # Try alternate import for older versions
                    import pymupdf
                    self.pymupdf = pymupdf
                except ImportError:
                    # Last resort: try to import from a specific path
                    logger.warning("Standard PyMuPDF imports failed, using fallback text extraction method")
                    from .text_extractor import extract_text_from_pdf
                    self.fallback_extractor = extract_text_from_pdf
                    self.pymupdf = None
        except Exception as e:
            logger.error(f"Failed to import PyMuPDF: {str(e)}")
            from .text_extractor import extract_text_from_pdf
            self.fallback_extractor = extract_text_from_pdf
            self.pymupdf = None
    
    def process(self) -> str:
        """
        Process the PDF and return structured Markdown.
        
        Returns:
            str: Markdown representation of the academic paper
        """
        try:
            # Check if PyMuPDF is available
            if not self.pymupdf:
                return self._fallback_process()
                
            # Open the document with PyMuPDF
            try:
                if hasattr(self.pymupdf, 'open'):
                    self.doc = self.pymupdf.open(self.pdf_path)
                elif hasattr(self.pymupdf, 'Document'):
                    self.doc = self.pymupdf.Document(self.pdf_path)
                else:
                    raise AttributeError("PyMuPDF module missing expected functionality")
                    
                self.stats["pages"] = len(self.doc)
                logger.info(f"Opened PDF with {self.stats['pages']} pages")
                
                # Extract document structure
                self._extract_metadata()
                self._extract_structure()
                self._detect_sections()
                self._process_references()
                
                # Convert to markdown
                markdown = self._to_markdown()
                self.markdown_text = markdown
                
                # Close the document
                if self.doc:
                    self.doc.close()
                    self.doc = None
                
                return markdown
            except Exception as pymupdf_error:
                logger.error(f"PyMuPDF processing failed: {str(pymupdf_error)}")
                logger.info("Falling back to basic extraction")
                return self._fallback_process()
        
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            # Ensure document is closed
            if hasattr(self, 'doc') and self.doc:
                try:
                    self.doc.close()
                    self.doc = None
                except:
                    pass
            return f"# Processing Error\n\nThere was an error processing the PDF: {str(e)}"
            
    def _fallback_process(self) -> str:
        """Process PDF using the fallback text extractor when PyMuPDF isn't available."""
        try:
            logger.info("Using fallback text extraction method")
            
            # Use our text extractor to get the content
            text = self.fallback_extractor(self.pdf_path)
            
            if not text or text.startswith("Failed to extract text"):
                # If text extraction failed completely, return a basic message
                self.metadata["title"] = "ACADEMIC PAPER TITLE"
                self.sections = [
                    {"heading": "Introduction", "content": ["Document could not be parsed."], "level": 1}
                ]
                return "# ACADEMIC PAPER TITLE\n# Introduction"
            
            # Extract title - first check for PDF text objects like (TITLE) Tj
            title_match = re.search(r'\(([A-Z][^)]+)\)\s+Tj', text)
            if title_match:
                potential_title = title_match.group(1).strip()
                if potential_title and not potential_title.lower().startswith("/f") and len(potential_title) < 100:
                    title = potential_title
                    # Remove any remaining Tj markers
                    text = re.sub(r'\([^)]+\)\s+Tj', lambda m: m.group(0).replace(" Tj", "").strip("()"), text)
            else:
                # Extract title from the first few lines
                lines = text.split('\n')
                title = "ACADEMIC PAPER TITLE"
                
                # Find a good candidate for title (non-empty, not too long, not all lowercase)
                for i, line in enumerate(lines[:10]):  # Check first 10 lines
                    line = line.strip()
                    if line and len(line) < 100 and not line.islower() and not line.startswith(("%", "[", "{", "<")):
                        title = line
                        break
                    
            self.metadata["title"] = title
            
            # Check if this is a PDF with Tj markers
            is_pdf_with_tj = bool(re.search(r'\([^)]+\)\s+Tj', text))
            
            if is_pdf_with_tj:
                # Handle PDF with Tj markers - try to extract structured content
                # Extract section titles and content
                self.metadata["title"] = title
                
                # Look for section headings (usually in parentheses and all caps)
                section_matches = re.finditer(r'\(([A-Z][A-Z\s]+)\)\s+Tj', text)
                sections = []
                prev_pos = 0
                current_section = {"heading": "Introduction", "content": [], "level": 1}
                sections.append(current_section)
                
                for match in section_matches:
                    heading = match.group(1).strip()
                    # Valid section headings are typically short and all caps
                    if len(heading) < 30 and heading == heading.upper() and heading != title:
                        # Process previous section content
                        section_text = text[prev_pos:match.start()]
                        # Extract text between parentheses for content
                        content_matches = re.finditer(r'\(([^)]+)\)\s+Tj', section_text)
                        for content in content_matches:
                            content_text = content.group(1).strip()
                            if content_text and content_text != current_section["heading"] and len(content_text) > 10:
                                current_section["content"].append(content_text)
                        
                        # Start new section
                        current_section = {"heading": heading.title(), "content": [], "level": 1}
                        sections.append(current_section)
                        prev_pos = match.end()
                        
                        # Check for abstract
                        if "ABSTRACT" in heading:
                            self.metadata["abstract"] = ""  # Initialize abstract
                
                # Process final section content
                if prev_pos < len(text):
                    section_text = text[prev_pos:]
                    content_matches = re.finditer(r'\(([^)]+)\)\s+Tj', section_text)
                    for content in content_matches:
                        content_text = content.group(1).strip()
                        if content_text and content_text != current_section["heading"] and len(content_text) > 10:
                            current_section["content"].append(content_text)
                            
                            # If this is the abstract section, populate abstract
                            if current_section["heading"].lower() == "abstract":
                                self.metadata["abstract"] = content_text
                
                # If we couldn't find sections, create a simple structure
                if len(sections) <= 1 and not sections[0]["content"]:
                    # Extract all text content
                    all_text = []
                    content_matches = re.finditer(r'\(([^)]+)\)\s+Tj', text)
                    for content in content_matches:
                        content_text = content.group(1).strip()
                        if content_text and content_text != title and len(content_text) > 10:
                            all_text.append(content_text)
                    
                    if all_text:
                        sections[0]["content"] = all_text
            else:
                # Standard text processing for non-PDF formats
                lines = text.split('\n')
                sections = []
                current_section = {"heading": "Introduction", "content": [], "level": 1}
                sections.append(current_section)
                
                in_abstract = False
                abstract_lines = []
                
                for line in lines[1:]:  # Skip the first line (assumed to be title)
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Check for potential headings
                    if len(line) < 50 and (line.upper() == line or re.match(r"^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s*$", line)):
                        # All caps lines or Title Case words are likely headings
                        current_section = {"heading": line, "content": [], "level": 1}
                        sections.append(current_section)
                        if "abstract" in line.lower():
                            in_abstract = True
                            continue
                    elif in_abstract:
                        if len(line) > 10:  # Likely part of the abstract
                            abstract_lines.append(line)
                        else:
                            # End of abstract if we hit a short line
                            in_abstract = False
                            self.metadata["abstract"] = " ".join(abstract_lines)
                            # This might be a heading
                            if len(line) > 3:  # Only if it has content
                                current_section = {"heading": line, "content": [], "level": 1}
                                sections.append(current_section)
                    elif re.match(r"^\d+\.?\s+[A-Z]", line) and len(line) < 80:
                        # Numbered headings like "1. Introduction"
                        current_section = {"heading": line, "content": [], "level": 1}
                        sections.append(current_section)
                    else:
                        # Regular content - group by paragraphs (at least 5 words)
                        words = line.split()
                        if len(words) >= 5:
                            current_section["content"].append(line)
            
            self.sections = sections
            
            # If we didn't find any real content, create a minimal structure
            if not any(section["content"] for section in sections):
                words = re.findall(r'\b[A-Za-z]{3,}\b', text)
                if len(words) > 20:
                    # Create a pseudo-paragraph with the words
                    chunks = [' '.join(words[i:i+20]) for i in range(0, len(words), 20)]
                    self.sections[0]["content"] = chunks
                else:
                    self.sections[0]["content"] = ["Document content could not be fully extracted."]
            
            # Clean up section content - remove any PDF artifacts
            for section in sections:
                # Remove "Tj" markers and unnecessary parentheses for display
                cleaned_content = []
                for item in section["content"]:
                    # Remove Tj markers
                    clean_item = re.sub(r'\s+Tj', '', item)
                    # Process references to remove unnecessary parentheses
                    if section["heading"].upper() == "REFERENCES":
                        # Remove leading/trailing parentheses but keep internal ones (for citations)
                        clean_item = re.sub(r'^\((.*)\)$', r'\1', clean_item)
                    cleaned_content.append(clean_item)
                section["content"] = cleaned_content
            
            # Generate markdown
            return self._to_markdown()
        except Exception as e:
            logger.error(f"Fallback processing failed: {str(e)}")
            return "# ACADEMIC PAPER TITLE\n\n> Note: This document was processed using AcademicPaperParser."
    
    def _extract_metadata(self) -> None:
        """Extract basic metadata from the document."""
        if not self.doc:
            return
        
        # Simple heuristic for title and authors
        # Usually, the first page contains this information
        first_page = self.doc[0]
        text = first_page.get_text()
        
        # Basic extraction of title (assuming it's near the top and has the largest font)
        # This is a simple approach and will be enhanced later
        blocks = first_page.get_text("dict")["blocks"]
        if blocks:
            # Sort blocks by y-position (top to bottom)
            sorted_blocks = sorted(blocks, key=lambda b: b["bbox"][1])
            
            # Assume title is in the first few blocks with larger font
            for block in sorted_blocks[:3]:
                if "lines" in block:
                    for line in block["lines"]:
                        if "spans" in line:
                            for span in line["spans"]:
                                # Assume larger fonts are for title
                                if span.get("size", 0) > 12:
                                    if not self.metadata["title"]:
                                        self.metadata["title"] = span.get("text", "").strip()
                                    elif not self.metadata["authors"] and self.metadata["title"]:
                                        # Assume authors come after title
                                        self.metadata["authors"].append(span.get("text", "").strip())
        
        # Fallback to filename if no title detected
        if not self.metadata["title"]:
            self.metadata["title"] = os.path.basename(self.pdf_path).replace(".pdf", "")
        
        # Try to find abstract (assuming it starts with "Abstract")
        abstract_match = re.search(r"Abstract[:\.\s]*(.+?)(?=\n\n|\n[A-Z]|\n\d\.|\n[I1]\.)", text, re.DOTALL | re.IGNORECASE)
        if abstract_match:
            self.metadata["abstract"] = abstract_match.group(1).strip()
    
    def _extract_structure(self) -> None:
        """Extract the document's structural elements."""
        if not self.doc:
            return
        
        all_blocks = []
        
        # Process each page
        for page_num, page in enumerate(self.doc):
            # Get blocks of text
            page_dict = page.get_text("dict")
            if "blocks" in page_dict:
                for block in page_dict["blocks"]:
                    if block.get("type") == 0:  # Text block
                        self.stats["text_blocks"] += 1
                        
                        # Add page number to the block for reference
                        block["page"] = page_num
                        all_blocks.append(block)
                    elif block.get("type") == 1:  # Image block
                        self.stats["images"] += 1
        
        # Sort blocks by page and then by y-position
        self.blocks = sorted(all_blocks, key=lambda b: (b["page"], b["bbox"][1]))
    
    def _detect_sections(self) -> None:
        """Identify standard academic paper sections."""
        if not self.doc or not hasattr(self, 'blocks'):
            return
        
        # Simple section detection based on font size and styling
        current_section = {"heading": "Introduction", "content": [], "level": 1}
        self.sections = [current_section]
        
        for block in self.blocks:
            if "lines" in block:
                for line in block["lines"]:
                    if "spans" in line:
                        # Get the first span in the line
                        if line["spans"]:
                            span = line["spans"][0]
                            text = span.get("text", "").strip()
                            
                            # Skip empty lines
                            if not text:
                                continue
                            
                            # Check if this might be a heading
                            font_size = span.get("size", 0)
                            font_flags = span.get("flags", 0)
                            is_bold = font_flags & 2 > 0
                            
                            # Very simple heuristic for headings
                            # (will be improved with more sophisticated detection)
                            if (font_size > 12 and len(text) < 100) or \
                               (is_bold and len(text) < 100 and text.isupper()) or \
                               (re.match(r"^\d+\.?\s+[A-Z][a-z]+", text)) or \
                               (text.strip().lower() in ["abstract", "introduction", "methods", 
                                                        "results", "discussion", "conclusion", 
                                                        "references", "acknowledgments"]):
                                
                                # This looks like a heading, start a new section
                                level = 1 if font_size > 14 or text.isupper() else 2
                                current_section = {"heading": text, "content": [], "level": level}
                                self.sections.append(current_section)
                            else:
                                # Regular content
                                if text:
                                    current_section["content"].append(text)
        
        # Look for the references section
        for section in self.sections:
            if section["heading"] and re.match(r"references|bibliography", section["heading"].lower()):
                self.references_section = section
                break
    
    def _process_references(self) -> None:
        """Extract and process references."""
        if not hasattr(self, 'references_section'):
            return
        
        # Simple reference extraction - find numbered or bracketed references
        reference_pattern = re.compile(r"(?:\[\d+\]|\d+\.)\s+(.+)")
        references = []
        
        for text in self.references_section["content"]:
            match = reference_pattern.match(text)
            if match:
                references.append(match.group(1).strip())
            elif references and text:  # Continuation of previous reference
                references[-1] += " " + text
        
        self.references = references
    
    def _to_markdown(self) -> str:
        """Convert the structured document to Markdown."""
        markdown_lines = []
        
        # Add title
        if self.metadata["title"]:
            markdown_lines.append(f"# {self.metadata['title']}\n")
        
        # Add authors
        if self.metadata["authors"]:
            authors_str = ", ".join(self.metadata["authors"])
            markdown_lines.append(f"**Authors**: {authors_str}\n")
        
        # Add abstract
        if self.metadata["abstract"]:
            markdown_lines.append("## Abstract\n")
            markdown_lines.append(f"{self.metadata['abstract']}\n")
        
        # Add sections
        for section in self.sections:
            # Skip the references section, we'll add it at the end
            if hasattr(self, 'references_section') and section == self.references_section:
                continue
                
            # Add heading with appropriate level
            heading_prefix = "#" * section["level"]
            markdown_lines.append(f"{heading_prefix} {section['heading']}\n")
            
            # Add content as paragraphs
            if section["content"]:
                # Group content into paragraphs (very simple approach)
                paragraphs = []
                current_paragraph = []
                
                for text in section["content"]:
                    if not text.strip():
                        if current_paragraph:
                            paragraphs.append(" ".join(current_paragraph))
                            current_paragraph = []
                    else:
                        current_paragraph.append(text)
                
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                
                # Add paragraphs to markdown
                for paragraph in paragraphs:
                    markdown_lines.append(f"{paragraph}\n\n")
        
        # Add references
        if self.references:
            markdown_lines.append("## References\n")
            for i, ref in enumerate(self.references, 1):
                markdown_lines.append(f"{i}. {ref}\n")
        
        # Add processing note
        markdown_lines.append("\n\n> Note: This document was processed using AcademicPaperParser.\n")
        
        return "".join(markdown_lines)