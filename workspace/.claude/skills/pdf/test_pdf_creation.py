#!/usr/bin/env python3
"""Quick test of PDF creation capabilities"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pypdf import PdfReader
import os

def create_test_pdf():
    """Create a simple test PDF"""
    output_file = "/tmp/test_pdf_skill.pdf"

    # Create PDF
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter

    # Add text
    c.drawString(100, height - 100, "PDF Skill Test Document")
    c.drawString(100, height - 120, "Created by Anthropic's PDF Skill")
    c.drawString(100, height - 140, "This demonstrates PDF creation with reportlab")

    # Add a line
    c.line(100, height - 160, 400, height - 160)

    # Add more text
    c.drawString(100, height - 200, "PDF processing capabilities:")
    c.drawString(120, height - 220, "- Create PDFs from scratch")
    c.drawString(120, height - 240, "- Extract text and tables")
    c.drawString(120, height - 260, "- Merge and split documents")
    c.drawString(120, height - 280, "- Fill forms (fillable and non-fillable)")
    c.drawString(120, height - 300, "- Add watermarks and encryption")

    # Save
    c.save()

    # Verify it works
    reader = PdfReader(output_file)
    print(f"✅ PDF created successfully!")
    print(f"   Location: {output_file}")
    print(f"   Pages: {len(reader.pages)}")
    print(f"   Size: {os.path.getsize(output_file)} bytes")

    # Extract text to verify
    text = reader.pages[0].extract_text()
    print(f"\n📄 Extracted text preview:")
    print(text[:200] + "...")

    return output_file

if __name__ == "__main__":
    create_test_pdf()
