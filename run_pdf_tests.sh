#\!/bin/bash
# Run the PDF conversion tests

# Activate the virtual environment
. venv/bin/activate

# Install test requirements if needed
pip install -r tests/requirements.txt

# Run the download script (uncomment when ready to download real papers)
# python tests/download_sample_papers.py

# Run the original conversion tests
echo "Running original PDF conversion tests..."
python tests/test_pdf_conversion.py

# Run the new academic parser tests
echo -e "\nRunning enhanced academic parser tests..."
python test_academic_parser.py tests/pdf_corpus/papers

# Visualize the results of one test paper with the original parser
echo -e "\nVisualizing test_paper results with original parser..."
python tests/visualize_conversion.py test_paper

# Compare with a real academic paper
echo -e "\nComparing original vs academic parser on a real paper..."
# Find first academic paper in corpus
FIRST_PAPER=$(find tests/pdf_corpus/papers -name "*.pdf" -not -path "*/test/*" | head -1)
if [ -n "$FIRST_PAPER" ]; then
  PAPER_NAME=$(basename "$FIRST_PAPER" .pdf)
  echo "Paper: $PAPER_NAME"
  echo -e "\nOriginal parser output (first 10 lines):"
  head -10 "tests/pdf_corpus/outputs/${PAPER_NAME}.md"
  echo -e "\nAcademic parser output (first 10 lines):"
  head -10 "${PAPER_NAME}_academic.md" 2>/dev/null || echo "Academic parser output not found"
else
  echo "No academic papers found in the corpus"
fi
