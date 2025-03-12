"""
Minimal test script for LlamaParse, following the example exactly.
"""
import os
import nest_asyncio
from dotenv import load_dotenv

# Apply nest_asyncio
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Set API key
api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
print(f"Using API key: {api_key[:5]}...")

# Import LlamaParse
from llama_parse import LlamaParse

# Create parser with default settings
parser = LlamaParse(
    api_key=api_key,
    result_type="markdown"
)

# Parse PDF
documents = parser.load_data("tests/pdf_corpus/papers/cs/attention_is_all_you_need.pdf")

# Save and check output
output_file = "simple_output.md"
with open(output_file, "w") as f:
    f.write(documents[0].text)

print(f"Output saved to {output_file}")
print(f"Output length: {len(documents[0].text)} characters")

# Check number of pages
page_separator = "\n---\n"
pages = documents[0].text.split(page_separator)
print(f"Number of pages detected: {len(pages)}")

# Print start of each page
for i, page in enumerate(pages[:3]):  # Show first 3 pages
    print(f"\nPage {i+1} (first 100 chars): {page[:100]}...")