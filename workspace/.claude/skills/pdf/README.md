# PDF Processing Skill

**Source:** Anthropic's Official Skills Repository
**Added:** 2025-11-30
**License:** Proprietary (see LICENSE.txt)

## Overview

Comprehensive PDF manipulation toolkit for:
- Extracting text and tables
- Creating new PDFs from scratch
- Merging/splitting documents
- Handling PDF forms (fillable and non-fillable)
- Adding watermarks and encryption
- OCR for scanned documents

## Installation

A dedicated virtual environment has been created for this skill:

```bash
# Virtual environment location
/root/software/.claude/skills/pdf/venv/

# Installed libraries
pypdf 6.4.0          # Core PDF operations
pdfplumber 0.11.8    # Text/table extraction
reportlab 4.4.5      # PDF creation
pdf2image 1.17.0     # PDF to image conversion
pypdfium2 5.1.0      # Fast rendering
pandas 2.3.3         # Table data processing
```

## Quick Start

### Using the Skill in Python

```python
# Activate the skill's virtual environment first
# /root/software/.claude/skills/pdf/venv/bin/python

from pypdf import PdfReader, PdfWriter
import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Read PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = reader.pages[0].extract_text()

# Create PDF
c = canvas.Canvas("output.pdf", pagesize=letter)
c.drawString(100, 750, "Hello World!")
c.save()
```

## Available Scripts

All scripts located in `/root/software/.claude/skills/pdf/scripts/`:

### Form Processing
- `check_fillable_fields.py` - Check if PDF has fillable fields
- `extract_form_field_info.py` - Extract form field metadata
- `fill_fillable_fields.py` - Fill fillable form fields
- `fill_pdf_form_with_annotations.py` - Fill non-fillable forms

### Utilities
- `convert_pdf_to_images.py` - Convert PDF pages to PNG images
- `create_validation_image.py` - Create validation images for form bounding boxes
- `check_bounding_boxes.py` - Validate bounding box intersections

## Documentation

1. **SKILL.md** - Main guide with quick start and common operations
2. **forms.md** - Detailed PDF form filling instructions (fillable & non-fillable)
3. **reference.md** - Advanced features and JavaScript libraries
4. **requirements.txt** - Python dependencies

## Usage in Claude Code

This skill is automatically discovered by Claude Code when you mention:
- "PDF" operations
- "fill a form"
- "extract text from PDF"
- "create PDF"
- "merge PDFs"

Claude will load this skill and use the appropriate tools and workflows.

## Test

A test script is available to verify the installation:

```bash
/root/software/.claude/skills/pdf/venv/bin/python /root/software/.claude/skills/pdf/test_pdf_creation.py
```

This creates a test PDF at `/tmp/test_pdf_skill.pdf` and verifies:
- PDF creation works
- Text extraction works
- All libraries are properly installed

## Common Tasks

### Extract Text
```python
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

### Extract Tables
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            df = pd.DataFrame(table[1:], columns=table[0])
            print(df)
```

### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("Report Title", styles['Title']))
story.append(Paragraph("Page 1 content", styles['Normal']))
story.append(PageBreak())
story.append(Paragraph("Page 2", styles['Heading1']))

doc.build(story)
```

## Command-Line Tools

The skill also documents command-line tools (install separately if needed):

- `pdftotext` (poppler-utils) - Extract text
- `qpdf` - Merge, split, rotate, decrypt
- `pdftk` - Merge, split, rotate
- `pdfimages` - Extract images

## Integration with Other Skills

This PDF skill can work alongside:
- **google-drive-operations** - Upload/download PDFs to Google Drive
- **azure-devops-git** - Version control for PDF documents
- **testing-workflows** - Test PDF generation pipelines

## Troubleshooting

### Import Errors
Always use the skill's virtual environment:
```bash
/root/software/.claude/skills/pdf/venv/bin/python your_script.py
```

### Missing Dependencies
Reinstall in the venv:
```bash
/root/software/.claude/skills/pdf/venv/bin/pip install -r /root/software/.claude/skills/pdf/requirements.txt
```

### Form Filling Issues
Follow the **exact workflow** in `forms.md`:
1. Check if form has fillable fields
2. Extract field info
3. Convert to images for visual analysis
4. Fill fields with validated data

## Resources

- **Official Anthropic Skills Repo:** https://github.com/anthropics/skills
- **pypdf Documentation:** https://pypdf.readthedocs.io/
- **pdfplumber Documentation:** https://github.com/jsvine/pdfplumber
- **reportlab Documentation:** https://www.reportlab.com/docs/reportlab-userguide.pdf

## License

This skill is proprietary. See `LICENSE.txt` for complete terms.

---

**Status:** ✅ Installed and tested
**Last Updated:** 2025-11-30
