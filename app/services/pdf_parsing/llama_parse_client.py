"""
LlamaParse Client

Integration with LlamaParse API through LlamaCloud with fallback methods.
"""
import os
import time
import logging
import json
import nest_asyncio
from typing import Optional, Dict, Any, List, Union, Tuple
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

# Apply nest_asyncio to support async operations in non-async environments
nest_asyncio.apply()

# Import the structured extractor
try:
    from .structured_extractor import extract_structured_data
    HAS_STRUCTURED_EXTRACTOR = True
except ImportError:
    logger.warning("Structured extractor not available. Some features may be limited.")
    HAS_STRUCTURED_EXTRACTOR = False

class LlamaParseClient:
    """Client for working with PDF parsing functionalities through LlamaParse."""
    
    # Default parsing instruction for academic papers
    DEFAULT_ACADEMIC_PAPER_INSTRUCTION = """
    The provided document is an academic research paper or scientific publication.
    
    Please ensure:
    1. Include ALL the original text with no summarization or omissions
    2. Preserve the hierarchical structure of sections and subsections exactly as they appear
    3. Handle multiple columns properly, maintaining correct reading order
    4. Extract tables and figures with their captions in full
    5. Format mathematical equations in LaTeX (between $ symbols)
    6. Preserve all citations and references exactly as they appear
    7. Distinguish between abstract, main content, and footnotes
    8. Properly identify section headings and maintain their hierarchy
    9. Extract metadata like title, authors, and publication details
    
    IMPORTANT: Do NOT summarize sections or content. Preserve ALL original text verbatim while maintaining structure.
    Focus on producing a complete, well-structured conversion that captures every detail of the original document.
    """
    
    def __init__(self, api_key: Optional[str] = None, result_type: str = "markdown", 
                 parsing_instruction: Optional[str] = None, use_academic_instruction: bool = True):
        """
        Initialize the client.
        
        Args:
            api_key: LlamaCloud API key. If not provided, will look for 
                   LLAMA_CLOUD_API_KEY in environment variables.
            result_type: Default output format ("markdown", "json", or "text")
            parsing_instruction: Optional custom instructions to guide the parsing process
            use_academic_instruction: Whether to use the default academic paper instruction
                                     if no custom instruction is provided
        """
        self.api_key = api_key or os.environ.get("LLAMA_CLOUD_API_KEY")
        self.result_type = result_type
        
        # Use custom instruction if provided, otherwise use academic paper instruction if requested
        if parsing_instruction:
            self.parsing_instruction = parsing_instruction
        elif use_academic_instruction:
            self.parsing_instruction = self.DEFAULT_ACADEMIC_PAPER_INSTRUCTION.strip()
        else:
            self.parsing_instruction = None
        
        # Check if we can import PyMuPDF for fallback
        self.has_pymupdf = False
        try:
            import fitz  # PyMuPDF
            self.has_pymupdf = True
        except ImportError:
            logger.warning("PyMuPDF not available for fallback. Ensure it's installed.")
    
    def parse_pdf(self, pdf_path: str, output_format: Optional[str] = None, return_structured: bool = False) -> Union[str, Tuple[str, Dict[str, Any]]]:
        """
        Parse a PDF file using LlamaParse or fallback methods.
        
        Note: The LlamaParse API currently extracts abstracts and basic metadata
        but may not extract the full text of all sections for complex academic papers.
        The system will fall back to local extraction methods when possible for
        more complete content extraction.
        
        Args:
            pdf_path: Path to the PDF file to parse
            output_format: Output format ("markdown", "json", or "text").
                          If not provided, uses the format specified at initialization.
            return_structured: If True, returns a tuple of (text, structured_data)
                             where structured_data contains title, authors, abstract, etc.
            
        Returns:
            str or tuple: Parsed content in the requested format, optionally with structured data
        """
        # Use the class-level result_type if no specific format is provided
        if output_format is None:
            output_format = self.result_type
            
        logger.info(f"Parsing PDF: {pdf_path}")
        start_time = time.time()
        
        try:
            # Check if we have a LlamaParse API key
            if self.api_key:
                # Use DirectLlamaClient first, which provides more complete content
                try:
                    # Try the direct API implementation which produces more complete results
                    from .direct_llama_client import DirectLlamaClient
                    
                    logger.info("Using DirectLlamaClient (primary method)")
                    direct_client = DirectLlamaClient(api_key=self.api_key)
                    
                    # Process using the direct client
                    result = direct_client.parse_pdf(
                        pdf_path=pdf_path,
                        output_format=output_format,
                        parsing_instruction=self.parsing_instruction
                    )
                    
                    processing_time = time.time() - start_time
                    logger.info(f"PDF parsing with DirectLlamaClient completed in {processing_time:.2f} seconds")
                    
                    # Handle structured data extraction if requested and available
                    if return_structured and output_format in ["markdown", "text"] and HAS_STRUCTURED_EXTRACTOR:
                        try:
                            logger.info("Extracting structured data from parsed content")
                            structured_data = extract_structured_data(result)
                            logger.info(f"Extracted structured data with {len(structured_data.get('sections', []))} sections")
                            return result, structured_data
                        except Exception as extract_error:
                            logger.error(f"Error extracting structured data: {str(extract_error)}")
                            # Fall back to returning just the result
                            return result
                    
                    return result
                    
                except Exception as direct_error:
                    logger.error(f"Error with DirectLlamaClient: {str(direct_error)}")
                    logger.info("Falling back to official LlamaParse package...")
                    
                    try:
                        # Import here to handle cases where the package isn't installed
                        from llama_parse import LlamaParse
                        
                        logger.warning("Using official LlamaParse client (fallback - may produce truncated results)")
                        parser = LlamaParse(
                            api_key=self.api_key,
                            result_type=output_format,
                            system_prompt="You are an academic paper parser. Extract the complete text of the document preserving all sections, tables, figures, and mathematical formulas. Do not summarize or omit any content. Keep the exact structure of the paper.",
                            system_prompt_append=self.parsing_instruction
                        )
                        
                        # Parse the document
                        documents = parser.load_data(pdf_path)
                        if not documents:
                            raise ValueError("No documents returned from LlamaParse")
                            
                        # Get the content from the first document
                        result = documents[0].text
                        logger.info(f"LlamaParse raw result length: {len(result)} characters")
                        
                        # Handle potential JSON-wrapped content
                        if output_format in ["markdown", "text"] and isinstance(result, str):
                            if result.startswith('{') and result.endswith('}'):
                                try:
                                    data = json.loads(result)
                                    logger.info(f"JSON result keys: {list(data.keys())}")
                                    
                                    if "markdown" in data:
                                        logger.info("Extracting markdown content from JSON response")
                                        result = data["markdown"]
                                        logger.info(f"Extracted markdown length: {len(result)} characters")
                                    elif output_format in data:
                                        logger.info(f"Extracting {output_format} content from JSON response")
                                        result = data[output_format]
                                        logger.info(f"Extracted content length: {len(result)} characters")
                                except json.JSONDecodeError as e:
                                    logger.warning(f"Failed to parse JSON result: {str(e)}")
                                    # Not valid JSON, keep original result
                                    pass
                        
                        # Log detailed info about the result
                        if isinstance(result, str):
                            line_count = result.count('\n') + 1
                            logger.info(f"Final result: {len(result)} characters, {line_count} lines")
                            logger.info(f"First 100 chars: {result[:100].replace(chr(10),'[LF]')}...")
                            logger.info(f"Last 100 chars: ...{result[-100:].replace(chr(10),'[LF]')}")
                        else:
                            logger.warning(f"Result is not a string but {type(result)}")
                        
                        processing_time = time.time() - start_time
                        logger.info(f"PDF parsing with LlamaParse completed in {processing_time:.2f} seconds")
                        
                        # Add a notice if the content is likely truncated
                        if len(result) < 5000 and output_format in ["markdown", "text"]:
                            logger.warning("The result appears truncated. Consider running only the DirectLlamaClient.")
                        
                        # Handle structured data extraction if requested and available
                        if return_structured and output_format in ["markdown", "text"] and HAS_STRUCTURED_EXTRACTOR:
                            try:
                                logger.info("Extracting structured data from parsed content")
                                structured_data = extract_structured_data(result)
                                logger.info(f"Extracted structured data with {len(structured_data.get('sections', []))} sections")
                                return result, structured_data
                            except Exception as extract_error:
                                logger.error(f"Error extracting structured data: {str(extract_error)}")
                                # Fall back to returning just the result
                                return result
                        
                        return result
                    
                    except Exception as package_error:
                        logger.error(f"Error with LlamaParse package: {str(package_error)}")
                        raise ValueError(f"Could not use either LlamaParse implementation: {str(direct_error)} / {str(package_error)}")
            else:
                logger.warning("No LlamaParse API key provided. Using fallback methods.")
                raise ValueError("LlamaParse API key not available")
                
        except Exception as llamaparse_error:
            logger.error(f"Error using LlamaParse API: {str(llamaparse_error)}")
            logger.info("Falling back to local processing methods...")
            
            # Use the locally available AcademicPaperParser as fallback
            if self.has_pymupdf:
                try:
                    from .academic_parser import AcademicPaperParser
                    
                    logger.info("Using local AcademicPaperParser as fallback")
                    parser = AcademicPaperParser(pdf_path)
                    result = parser.process()
                    
                    # If JSON format is requested, convert the markdown to JSON
                    if output_format == "json":
                        metadata = {
                            "title": parser.metadata.get("title", ""),
                            "authors": parser.metadata.get("authors", []),
                            "abstract": parser.metadata.get("abstract", ""),
                            "sections": [
                                {"title": section.get("title", ""), "level": section.get("level", 1)}
                                for section in parser.sections
                            ],
                            "content": result
                        }
                        return json.dumps(metadata, indent=2)
                    
                    processing_time = time.time() - start_time
                    logger.info(f"PDF parsing with fallback completed in {processing_time:.2f} seconds")
                    
                    # Handle structured data extraction if requested and available
                    if return_structured and output_format in ["markdown", "text"] and HAS_STRUCTURED_EXTRACTOR:
                        try:
                            logger.info("Extracting structured data from parsed content")
                            structured_data = extract_structured_data(result)
                            logger.info(f"Extracted structured data with {len(structured_data.get('sections', []))} sections")
                            return result, structured_data
                        except Exception as extract_error:
                            logger.error(f"Error extracting structured data: {str(extract_error)}")
                            # Fall back to returning just the result
                            return result
                    
                    return result
                    
                except Exception as fallback_error:
                    logger.error(f"Error with fallback parser: {str(fallback_error)}")
                    raise ValueError(f"All parsing methods failed: {str(fallback_error)}")
            else:
                logger.error("No fallback methods available. Please ensure PyMuPDF is installed.")
                raise ValueError("No parsing methods available")
    
    @staticmethod
    def extract_metadata(parsed_output: str, output_format: str = "markdown") -> Dict[str, Any]:
        """
        Extract metadata from the parsed output.
        
        Args:
            parsed_output: The output from parse_pdf
            output_format: The format of the parsed output
            
        Returns:
            Dict: Metadata including title, authors, abstract, etc.
        """
        metadata = {
            "title": None,
            "authors": [],
            "abstract": None,
            "keywords": [],
            "sections": []
        }
        
        if output_format == "json":
            # If JSON, parse it and extract metadata directly
            try:
                if isinstance(parsed_output, str):
                    data = json.loads(parsed_output)
                else:
                    data = parsed_output
                
                # Extract basic metadata
                metadata["title"] = data.get("title")
                metadata["authors"] = data.get("authors", [])
                metadata["abstract"] = data.get("abstract")
                
                # Get sections
                if "sections" in data:
                    metadata["sections"] = [
                        {"title": section.get("title", ""), "level": section.get("level", 1)}
                        for section in data.get("sections", [])
                    ]
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON output")
        
        elif output_format in ["markdown", "text"]:
            # Simple extraction from markdown/text
            lines = parsed_output.split("\n")
            
            # Try to extract title (usually first heading)
            for line in lines:
                if line.startswith("# "):
                    metadata["title"] = line[2:].strip()
                    break
            
            # Try to extract authors (usually after title, may be in format **Authors:** or similar)
            for i, line in enumerate(lines):
                if "author" in line.lower() and ":" in line:
                    # Extract authors list from line like "**Authors:** Name1, Name2"
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        authors_text = parts[1].strip()
                        metadata["authors"] = [a.strip() for a in authors_text.split(",")]
                    break
            
            # Try to extract abstract (usually under ## Abstract heading)
            in_abstract = False
            abstract_lines = []
            
            for line in lines:
                if line.startswith("## Abstract"):
                    in_abstract = True
                    continue
                elif in_abstract and line.startswith("##"):
                    in_abstract = False
                    break
                elif in_abstract and line.strip():
                    abstract_lines.append(line)
            
            if abstract_lines:
                metadata["abstract"] = "\n".join(abstract_lines)
            
            # Extract section headings
            for line in lines:
                if line.startswith("#"):
                    # Count heading level and get title
                    level = 0
                    for char in line:
                        if char == "#":
                            level += 1
                        else:
                            break
                    
                    title = line[level:].strip()
                    if title:
                        metadata["sections"].append({"title": title, "level": level})
        
        return metadata