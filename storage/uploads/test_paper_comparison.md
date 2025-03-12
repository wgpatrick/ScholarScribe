# Parser Comparison for test_paper

## Processing Time

- **LlamaParse**: 0.13 seconds
- **Custom Parser**: 0.00 seconds

## Metadata Extraction

### LlamaParse Metadata

- **Title**: 
- **Authors**: 
- **Abstract**: ...
- **Sections**: 5

### Custom Parser Metadata

- **Title**: /F1 24 Tf
- **Authors**: 
- **Abstract**: ...
- **Sections**: 7

## Output Comparison

### LlamaParse Output (First 20 lines)

```markdown
# 

%PDF-1.4

1 0 obj

<< /Type /Catalog /Pages 2 0 R >>

endobj

2 0 obj

<< /Type /Pages /Kids [3 0 R] /Count 1 >>

endobj

3 0 obj

<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>

```

### Custom Parser Output (First 20 lines)

```markdown
# /F1 24 Tf
# Introduction
# (ACADEMIC PAPER TITLE)
(This is a sample academic paper for testing our PDF to Markdown conversion.)

# (INTRODUCTION)
(This section introduces the topic of our research.)

# (METHODOLOGY)
(In this section, we describe our research methods.)

# (RESULTS)
(Here we present the results of our study.)

# (CONCLUSION)
(Finally, we conclude with a summary of our findings.)

# (REFERENCES)
(1. Smith, J. (2022). A Study of Something. Journal of Studies, 15(2), 123-145.) (2. Johnson, A. (2021). Another Research Paper. Academic Review, 8(3), 234-256.)

```

## Qualitative Assessment

### Structure Preservation

- **LlamaParse**: [To be assessed]
- **Custom Parser**: [To be assessed]

### Multi-column Handling

- **LlamaParse**: [To be assessed]
- **Custom Parser**: [To be assessed]

### Table and Figure Handling

- **LlamaParse**: [To be assessed]
- **Custom Parser**: [To be assessed]

### Reference Processing

- **LlamaParse**: [To be assessed]
- **Custom Parser**: [To be assessed]

