# PDF Test Corpus

This directory contains academic papers for testing our PDF conversion pipeline.

## Directory Structure

- `papers/`: Contains categorized academic papers in PDF format
  - `cs/`: Computer Science papers
  - `bio/`: Biology/Life Sciences papers
  - `physics/`: Physics papers
  - `economics/`: Economics papers
  - `math/`: Mathematics papers

- `outputs/`: Contains the markdown output files from conversion

- `metrics/`: Contains evaluation metrics and comparison data

## How to Use

1. Add academic papers to the relevant category in the `papers/` directory
2. Run the evaluation script: `python tests/test_pdf_conversion.py`
3. Check the outputs in the `outputs/` directory
4. Review metrics in the `metrics/` directory

## Evaluation Metrics

The metrics files contain:
- Processing time
- Word count
- Line count
- Heading count
- Conversion status
- Timestamp

## Guidelines for Adding Papers

- Try to include diverse formats and layouts
- Include papers with different elements (tables, figures, math equations)
- Make sure to use papers that are freely available for testing
- Name files descriptively (e.g., "quantum_computing_nature_2020.pdf")
