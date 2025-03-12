"""
PDF Text Extractor

A simple utility to extract text from PDFs without using PyMuPDF directly.
"""
import os
import tempfile
import subprocess
import logging
import re

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using pdftotext if available,
    or a simple alternative method.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Extracted text
    """
    # First try to use pdftotext utility if available
    try:
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            try:
                subprocess.run(["pdftotext", pdf_path, tmp.name], check=True)
                with open(tmp.name, "r") as f:
                    text = f.read()
                    logger.info("Successfully extracted text using pdftotext")
                    return text
            except (subprocess.SubprocessError, FileNotFoundError):
                logger.info("pdftotext not available, trying alternative method")
    except Exception as e:
        logger.warning(f"Error during pdftotext extraction attempt: {str(e)}")
    
    # Try parsing text directly from the PDF
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_content = file.read()
            pdf_str = pdf_content.decode('latin-1')  # Use latin-1 to avoid encoding errors
            
            # Regular expressions to extract text streams from PDF
            # Look for text between "stream" and "endstream" markers
            stream_pattern = re.compile(r'stream\s+(.*?)\s+endstream', re.DOTALL)
            streams = stream_pattern.findall(pdf_str)
            
            # Process streams to extract text
            extracted_text = []
            for stream in streams:
                # Remove non-printable characters but keep spaces and line breaks
                cleaned = ''.join(c if c.isprintable() or c.isspace() else ' ' for c in stream)
                # Filter out lines containing actual text (more alphanumeric than special chars)
                lines = cleaned.split('\n')
                for line in lines:
                    # Count alphanumeric characters
                    alpha_count = sum(1 for c in line if c.isalnum())
                    # If the line has at least 3 characters and alphanumerics are more than 30%
                    if len(line.strip()) >= 3 and alpha_count / max(1, len(line)) > 0.3:
                        extracted_text.append(line.strip())
            
            text = '\n'.join(extracted_text)
            
            # If we couldn't extract meaningful text, fall back to simple approach
            if not text.strip():
                logger.info("Stream extraction yielded no results, using simple text search")
                # Look for text between parentheses followed by Tj (commonly used for text in PDFs)
                text_pattern = re.compile(r'\((.*?)\)[\s\r\n]*Tj', re.DOTALL)
                text_matches = text_pattern.findall(pdf_str)
                
                # Filter for meaningful text
                filtered_matches = []
                for match in text_matches:
                    # Skip single characters, likely not real text
                    if len(match) < 2:
                        continue
                    # Skip if not enough alphanumeric characters
                    if sum(c.isalnum() for c in match) < 2:
                        continue
                    # Skip if it looks like a date or time
                    if re.match(r'^\d{1,2}/\d{1,2}/\d{2,4}$', match) or re.match(r'^\d{1,2}:\d{1,2}(:\d{1,2})?$', match):
                        continue
                    filtered_matches.append(match)
                
                # If we found text content, assemble it into paragraphs
                if filtered_matches:
                    # Group text by potential paragraphs (longer strings likely complete sentences)
                    paragraphs = []
                    current_para = []
                    
                    for match in filtered_matches:
                        # If match is very short, it might be continuing a sentence
                        if len(match) < 20 and not match.endswith('.'):
                            current_para.append(match)
                        else:
                            current_para.append(match)
                            if match.endswith('.'):
                                paragraphs.append(' '.join(current_para))
                                current_para = []
                    
                    # Add any remaining text
                    if current_para:
                        paragraphs.append(' '.join(current_para))
                    
                    text = '\n\n'.join(paragraphs)
                else:
                    # If no Tj-marked text found, try a more general approach
                    text_pattern = re.compile(r'\((.*?)\)', re.DOTALL)
                    text_matches = text_pattern.findall(pdf_str)
                    
                    # More aggressive filtering
                    filtered_matches = []
                    for match in text_matches:
                        # Must have reasonable length
                        if len(match) < 5:
                            continue
                        # Must contain spaces (likely real text)
                        if ' ' not in match:
                            continue
                        # Skip if not enough alphanumeric characters
                        if sum(c.isalnum() for c in match) / len(match) < 0.5:
                            continue
                        filtered_matches.append(match)
                    
                    # Try to identify sections vs. paragraphs
                    sections = []
                    paragraphs = []
                    
                    for match in filtered_matches:
                        # Check if this might be a heading
                        if len(match) < 50 and match.strip().istitle() and not match.endswith('.'):
                            if paragraphs:
                                sections.append('\n\n'.join(paragraphs))
                                paragraphs = []
                            sections.append(f"\n## {match}\n")
                        else:
                            paragraphs.append(match)
                    
                    if paragraphs:
                        sections.append('\n\n'.join(paragraphs))
                    
                    text = '\n'.join(sections)
        
        # If we still couldn't extract text, try a very simple approach
        if not text.strip():
            logger.info("Falling back to basic text search")
            printable_chars = ''.join(c if (c.isprintable() or c.isspace()) and not c.isdigit() else ' ' for c in pdf_str)
            words = re.findall(r'[A-Za-z]{3,}', printable_chars)
            text = ' '.join(words)
        
        # Final cleanup - remove any remaining PDF operators
        text = re.sub(r'\s+Tj', '', text)
        
        return text
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return f"Failed to extract text: {str(e)}"