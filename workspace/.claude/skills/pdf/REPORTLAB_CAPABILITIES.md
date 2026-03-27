# ReportLab Capabilities - Comprehensive Guide

**Version:** 4.4.5
**Python Package:** reportlab
**Installation:** Already in `/root/software/.claude/skills/pdf/venv/`
**Last Updated:** 2025-11-30

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Core Modules](#core-modules)
3. [Graphics Primitives](#graphics-primitives)
4. [Charts and Graphs](#charts-and-graphs)
5. [Text and Typography](#text-and-typography)
6. [Advanced Features](#advanced-features)
7. [Examples](#examples)
8. [Limitations](#limitations)

---

## Overview

ReportLab is a powerful Python library for creating PDFs programmatically. It offers two main approaches:

1. **Low-level (Canvas API)** - Direct PDF drawing commands
2. **High-level (Platypus)** - Document templates and flowables

**Key Strengths:**
- ✅ Vector graphics (scalable, resolution-independent)
- ✅ Programmatic chart generation
- ✅ Complex layouts and tables
- ✅ Multi-page documents
- ✅ Custom fonts and styles
- ✅ Mathematical precision

**Limitations:**
- ❌ No emoji support (Unicode emojis render as squares)
- ❌ Limited raster image manipulation
- ❌ No interactive PDF features (forms have limited support)

---

## Core Modules

### 1. **pdfgen.canvas** - Low-Level PDF Generation

Direct PDF drawing commands for precise control.

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("output.pdf", pagesize=letter)
width, height = letter

# Draw text
c.drawString(100, height - 100, "Hello World!")

# Draw shapes
c.line(100, 100, 500, 100)  # x1, y1, x2, y2
c.rect(100, 200, 200, 100)  # x, y, width, height
c.circle(300, 400, 50)      # x, y, radius

# Save
c.save()
```

**Use Cases:**
- Precise positioning of elements
- Custom page layouts
- Direct control over PDF structure
- Simple documents with basic shapes

---

### 2. **platypus** - High-Level Document Templates

Document templates with automatic flow and pagination.

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("output.pdf")
story = []
styles = getSampleStyleSheet()

# Add content
story.append(Paragraph("Chapter 1", styles['Heading1']))
story.append(Spacer(1, 12))
story.append(Paragraph("Content here...", styles['BodyText']))
story.append(PageBreak())

# Build document
doc.build(story)
```

**Use Cases:**
- Multi-page reports
- Books and articles
- Automatic pagination
- Consistent styling

---

### 3. **graphics.shapes** - Vector Graphics Primitives

**Available Shapes (42 total):**

#### Basic Shapes:
- **Line** - Straight line between two points
- **Rect** - Rectangle with optional fill and stroke
- **Circle** - Perfect circle
- **Ellipse** - Oval shape
- **Polygon** - Multi-sided closed shape
- **PolyLine** - Multi-point open line
- **Wedge** - Pie slice / arc segment
- **Path** - Bezier curves and complex paths
- **ArcPath** - Curved arcs

#### Text:
- **String** - Single line of text with positioning

#### Images:
- **Image** - Embed raster images (PNG, JPG)

#### Grouping:
- **Group** - Container for multiple shapes
- **Drawing** - Top-level container for graphics

#### Advanced:
- **Hatching** - Pattern fills
- **EmptyClipPath** - Clipping regions

**Example:**
```python
from reportlab.graphics.shapes import Drawing, Circle, Rect, String
from reportlab.lib import colors

d = Drawing(400, 200)

# Add shapes
d.add(Rect(10, 10, 100, 50, fillColor=colors.blue))
d.add(Circle(200, 100, 30, fillColor=colors.red))
d.add(String(50, 150, "Hello!", fontSize=20))
```

---

### 4. **graphics.charts** - Charts and Graphs

ReportLab includes built-in charting capabilities:

#### Line Charts (7 types):
- **LineChart** - Basic line chart
- **VerticalLineChart** - Vertical orientation
- **HorizontalLineChart** - Horizontal orientation
- **HorizontalLineChart3D** - 3D effect
- **AbstractLineChart** - Base class for custom charts

#### Bar Charts (8 types):
- **BarChart** - Basic bar chart
- **VerticalBarChart** - Vertical bars
- **HorizontalBarChart** - Horizontal bars
- **BarChart3D** - 3D bar chart
- **VerticalBarChart3D** - 3D vertical
- **HorizontalBarChart3D** - 3D horizontal

#### Pie Charts (1 type):
- **AbstractPieChart** - Pie/donut charts

#### Legends (5 types):
- **Legend** - Standard legend
- **LineLegend** - For line charts
- **LegendCallout** - With callout lines
- **LegendSwatchCallout** - Color swatches
- **LegendColEndCallout** - Column-end placement

**Example Line Chart:**
```python
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors

drawing = Drawing(400, 200)

lc = HorizontalLineChart()
lc.x = 50
lc.y = 50
lc.height = 125
lc.width = 300
lc.data = [
    [1, 2, 3, 5, 8, 13],
    [1, 3, 9, 27, 81, 243]
]
lc.categoryAxis.categoryNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
lc.lines[0].strokeColor = colors.blue
lc.lines[1].strokeColor = colors.red

drawing.add(lc)
```

---

### 5. **lib.colors** - Color Definitions

**195 named colors available:**

#### Standard Colors:
- red, blue, green, yellow, orange, purple, pink
- black, white, gray, grey
- brown, cyan, magenta

#### Extended Palette:
- aliceblue, antiquewhite, aqua, aquamarine
- azure, beige, bisque, blanchedalmond
- blueviolet, brown, burlywood, cadetblue
- chartreuse, chocolate, coral, cornflowerblue
- ... and 150+ more

#### Color Formats:
```python
from reportlab.lib import colors

# Named colors
color1 = colors.red
color2 = colors.dodgerblue

# RGB (0-1 scale)
color3 = colors.Color(0.5, 0.5, 0.5)  # Gray

# Hex colors
color4 = colors.HexColor('#FF5733')

# CMYK
color5 = colors.CMYKColor(0, 1, 1, 0)  # Red in CMYK

# With alpha (transparency)
color6 = colors.Color(1, 0, 0, alpha=0.5)  # Semi-transparent red
```

---

### 6. **lib.styles** - Text Styles

**Predefined Styles:**
- Heading1, Heading2, Heading3, Heading4, Heading5, Heading6
- Title, Subtitle
- BodyText, Normal
- Italic, Bold
- Definition
- Code
- Bullet, OrderedList, UnorderedList

**Custom Styles:**
```python
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

custom_style = ParagraphStyle(
    'CustomStyle',
    fontSize=12,
    textColor=colors.blue,
    alignment=TA_CENTER,
    spaceAfter=12,
    spaceBefore=6,
    leftIndent=20,
    rightIndent=20,
    fontName='Helvetica-Bold',
    leading=16  # Line height
)
```

---

### 7. **lib.units** - Measurement Units

```python
from reportlab.lib.units import inch, cm, mm, pica

# Common units
width = 8.5 * inch  # Letter width
height = 11 * inch  # Letter height

margin = 2.5 * cm
spacing = 10 * mm

# Pica (typography unit)
line_height = 1 * pica  # 12 points
```

**Available Units:**
- **inch** - 72 points (1 inch)
- **cm** - Centimeters
- **mm** - Millimeters
- **pica** - 12 points (1/6 inch)

---

## Graphics Primitives

### Shapes with Fill and Stroke

All shapes support:
- **fillColor** - Interior color
- **strokeColor** - Border color
- **strokeWidth** - Border thickness
- **strokeDashArray** - Dashed lines [dash_length, gap_length]

```python
from reportlab.graphics.shapes import Rect, Circle
from reportlab.lib import colors

# Rectangle with fill and border
rect = Rect(100, 100, 200, 100)
rect.fillColor = colors.lightblue
rect.strokeColor = colors.darkblue
rect.strokeWidth = 2

# Circle with dashed border
circle = Circle(300, 200, 50)
circle.fillColor = colors.red
circle.strokeColor = colors.black
circle.strokeWidth = 3
circle.strokeDashArray = [5, 3]  # 5pt dash, 3pt gap
```

---

### Path - Complex Shapes

Create custom shapes with Bezier curves:

```python
from reportlab.graphics.shapes import Path
from reportlab.lib import colors

path = Path(fillColor=colors.yellow, strokeColor=colors.red)

# Move to starting point
path.moveTo(100, 100)

# Draw lines
path.lineTo(200, 100)
path.lineTo(200, 200)

# Bezier curve
path.curveTo(200, 300, 100, 300, 100, 200)

# Close path
path.closePath()
```

---

### Polygon - Multi-sided Shapes

```python
from reportlab.graphics.shapes import Polygon
from reportlab.lib import colors

# Triangle
triangle = Polygon([100, 100, 200, 100, 150, 200])
triangle.fillColor = colors.green
triangle.strokeColor = colors.darkgreen

# Star (5 points)
star_points = [
    200, 100,  # Top
    220, 150,  # Right outer
    270, 150,  # Right point
    230, 180,  # Right inner
    250, 230,  # Bottom right
    200, 200,  # Bottom
    150, 230,  # Bottom left
    170, 180,  # Left inner
    130, 150,  # Left point
    180, 150,  # Left outer
]
star = Polygon(star_points, fillColor=colors.gold)
```

---

## Charts and Graphs

### Bar Chart Example

```python
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors

drawing = Drawing(400, 250)

bc = VerticalBarChart()
bc.x = 50
bc.y = 50
bc.height = 150
bc.width = 300

# Data
bc.data = [
    [5, 10, 15, 20, 25],  # Series 1
    [8, 12, 18, 22, 28],  # Series 2
]

# Categories
bc.categoryAxis.categoryNames = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']

# Styling
bc.bars[0].fillColor = colors.blue
bc.bars[1].fillColor = colors.red
bc.valueAxis.valueMin = 0
bc.valueAxis.valueMax = 30

drawing.add(bc)

# Render to PDF
from reportlab.graphics import renderPDF
renderPDF.drawToFile(drawing, 'chart.pdf', 'Bar Chart')
```

---

### Pie Chart Example

```python
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors

drawing = Drawing(400, 250)

pie = Pie()
pie.x = 150
pie.y = 65
pie.width = 100
pie.height = 100

# Data
pie.data = [20, 30, 15, 35]
pie.labels = ['Q1', 'Q2', 'Q3', 'Q4']

# Colors
pie.slices[0].fillColor = colors.blue
pie.slices[1].fillColor = colors.red
pie.slices[2].fillColor = colors.green
pie.slices[3].fillColor = colors.yellow

# Labels
pie.slices.strokeWidth = 0.5
pie.slices.fontName = 'Helvetica-Bold'
pie.slices.fontSize = 10

drawing.add(pie)
```

---

## Text and Typography

### Fonts Available

**Standard PDF Fonts (always available):**
- Helvetica (sans-serif)
- Helvetica-Bold
- Helvetica-Oblique
- Helvetica-BoldOblique
- Times-Roman (serif)
- Times-Bold
- Times-Italic
- Times-BoldItalic
- Courier (monospace)
- Courier-Bold
- Courier-Oblique
- Courier-BoldOblique

**Custom Fonts:**
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register TrueType font
pdfmetrics.registerFont(TTFont('CustomFont', '/path/to/font.ttf'))

# Use in document
canvas.setFont('CustomFont', 12)
canvas.drawString(100, 100, "Custom font text")
```

---

### Text Formatting

```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

# HTML-like markup in paragraphs
text = """
<b>Bold text</b> and <i>italic text</i> and <b><i>both</i></b>.
<font color="red">Red text</font> and <font size="20">big text</font>.
"""

style = ParagraphStyle('Normal')
p = Paragraph(text, style)
```

**Supported Tags:**
- `<b>` - Bold
- `<i>` - Italic
- `<u>` - Underline
- `<font>` - Font styling (color, size, face)
- `<br/>` - Line break
- `<sup>` - Superscript
- `<sub>` - Subscript

---

## Advanced Features

### Tables

```python
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

data = [
    ['Header 1', 'Header 2', 'Header 3'],
    ['Row 1 Col 1', 'Row 1 Col 2', 'Row 1 Col 3'],
    ['Row 2 Col 1', 'Row 2 Col 2', 'Row 2 Col 3'],
]

table = Table(data, colWidths=[2*inch, 2*inch, 2*inch])

table.setStyle(TableStyle([
    # Header row
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

    # Data rows
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]))
```

---

### Images

```python
from reportlab.platypus import Image

# Embed image
img = Image('/path/to/image.png', width=4*inch, height=3*inch)

# Or with canvas
from reportlab.pdfgen import canvas

c = canvas.Canvas("output.pdf")
c.drawImage('/path/to/image.png', 100, 500, width=200, height=150)
c.save()
```

**Supported Formats:**
- PNG (with transparency)
- JPEG
- GIF
- BMP

---

### Transformations

```python
# Rotate text
c.rotate(45)
c.drawString(100, 100, "Rotated 45°")

# Scale
c.scale(1.5, 1.5)  # 150% size

# Translate (move origin)
c.translate(100, 100)

# Skew
c.skew(0, 45)  # Skew vertically
```

---

### Watermarks

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("watermark.pdf", pagesize=letter)
width, height = letter

# Save state
c.saveState()

# Rotate and make transparent
c.setFillAlpha(0.1)
c.rotate(45)
c.setFont("Helvetica-Bold", 60)
c.drawString(200, 200, "DRAFT")

# Restore state
c.restoreState()

# Normal content
c.drawString(100, height - 100, "Document content")
c.save()
```

---

## Examples

### Example 1: Professional Invoice

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

doc = SimpleDocTemplate("invoice.pdf", pagesize=letter)
story = []
styles = getSampleStyleSheet()

# Header
story.append(Paragraph("INVOICE #12345", styles['Title']))
story.append(Paragraph("Date: November 30, 2025", styles['Normal']))

# Invoice data
invoice_data = [
    ['Item', 'Quantity', 'Price', 'Total'],
    ['Product A', '5', '$10.00', '$50.00'],
    ['Product B', '3', '$25.00', '$75.00'],
    ['Product C', '2', '$15.00', '$30.00'],
    ['', '', 'TOTAL:', '$155.00'],
]

invoice_table = Table(invoice_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
invoice_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('GRID', (0, 0), (-1, -2), 1, colors.black),
    ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
    ('BACKGROUND', (2, -1), (-1, -1), colors.lightgrey),
]))

story.append(invoice_table)
doc.build(story)
```

---

### Example 2: Dashboard with Charts

```python
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics import renderPDF

doc = SimpleDocTemplate("dashboard.pdf")
story = []
styles = getSampleStyleSheet()

# Title
story.append(Paragraph("Sales Dashboard - Q4 2025", styles['Title']))
story.append(Spacer(1, 12))

# Bar chart
bar_drawing = Drawing(400, 200)
bc = VerticalBarChart()
bc.x = 50
bc.y = 50
bc.height = 125
bc.width = 300
bc.data = [[100, 150, 200, 180]]
bc.categoryAxis.categoryNames = ['Oct', 'Nov', 'Dec', 'Jan']
bar_drawing.add(bc)
story.append(bar_drawing)

story.append(Spacer(1, 12))

# Pie chart
pie_drawing = Drawing(400, 200)
pie = Pie()
pie.x = 150
pie.y = 50
pie.width = 100
pie.height = 100
pie.data = [40, 30, 20, 10]
pie.labels = ['North', 'South', 'East', 'West']
pie_drawing.add(pie)
story.append(pie_drawing)

doc.build(story)
```

---

## Limitations

### What ReportLab CANNOT Do:

1. **Emoji Support** ❌
   - Unicode emojis render as black squares (■)
   - Solution: Use text symbols (•, ✓, ✗) or small PNG icons

2. **Interactive Forms** ⚠️
   - Limited form field support
   - Better to use pypdf for form filling

3. **Advanced Image Editing** ❌
   - No filters, effects, or transformations
   - Images are embedded as-is
   - Use PIL/Pillow for pre-processing

4. **HTML Rendering** ⚠️
   - Only basic HTML tags in Paragraphs
   - No CSS support
   - No complex layouts

5. **Right-to-Left Text** ⚠️
   - Limited support for RTL languages
   - Arabic, Hebrew may have issues

6. **Font Ligatures** ❌
   - No automatic ligatures (fi, fl, etc.)
   - Standard fonts only

---

## Best Practices

### 1. Use Appropriate API Level

- **Simple documents** → Canvas API
- **Multi-page reports** → Platypus
- **Charts** → graphics.charts
- **Custom graphics** → graphics.shapes

### 2. Performance

- Reuse Drawing objects when possible
- Use Groups for repeated elements
- Minimize font changes
- Cache complex calculations

### 3. Layout

- Use units (inch, cm) for consistency
- Define page templates for multi-page docs
- Use spacers for vertical spacing
- Test on different PDF readers

### 4. Styling

- Create style library for consistency
- Use named colors from reportlab.lib.colors
- Define constants for spacing/sizes
- Document custom styles

---

## Resources

- **Official Docs:** https://www.reportlab.com/docs/reportlab-userguide.pdf
- **GitHub:** https://github.com/MrBitBucket/reportlab-mirror
- **PyPI:** https://pypi.org/project/reportlab/
- **Skill Location:** `/root/software/.claude/skills/pdf/`

---

**Status:** ✅ Comprehensive reference complete
**Version:** reportlab 4.4.5
**Last Updated:** 2025-11-30
