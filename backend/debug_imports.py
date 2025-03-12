#!/usr/bin/env python
"""
This script helps debug import issues with PyMuPDF (fitz).
"""
import os
import sys
import platform

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Working directory: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

try:
    import fitz
    print(f"PyMuPDF (fitz) imported successfully: {fitz.__version__}")
    
    # Try to open a PDF
    test_pdf = "storage/uploads/test_paper.pdf"
    if os.path.exists(test_pdf):
        try:
            doc = fitz.open(test_pdf)
            print(f"Successfully opened PDF with {len(doc)} pages")
            # Try to extract text from first page
            if len(doc) > 0:
                text = doc[0].get_text()
                print(f"First 100 chars of text: {text[:100]}")
            doc.close()
        except Exception as e:
            print(f"Error opening PDF: {str(e)}")
    else:
        print(f"Test PDF not found at {test_pdf}")
    
except ImportError as e:
    print(f"Error importing fitz: {str(e)}")
    
    # Check if PyMuPDF is installed
    try:
        import pkg_resources
        print("\nInstalled packages:")
        for pkg in pkg_resources.working_set:
            if "mu" in pkg.key.lower() or "pdf" in pkg.key.lower():
                print(f"  {pkg.key} {pkg.version}")
    except Exception as pkg_e:
        print(f"Error checking packages: {str(pkg_e)}")