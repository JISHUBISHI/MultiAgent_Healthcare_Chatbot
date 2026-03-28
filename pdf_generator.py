"""
PDF Report Generator
Generates a beautifully formatted PDF report from HealthBuddy analysis results.
"""

import re
from datetime import datetime

from fpdf import FPDF


def pdf_safe_text(text: str, max_len: int | None = None) -> str:
    """Helvetica/core fonts only support Latin-1; avoid Unicode encode errors."""
    s = text if text is not None else ""
    s = s.encode("latin-1", "replace").decode("latin-1")
    # Break long unbroken words to avoid "Not enough horizontal space" errors in multi_cell
    s = re.sub(r'(\S{60})', r'\1 ', s)
    if max_len is not None:
        s = s[:max_len]
    return s


class HealthcarePDF(FPDF):
    """Custom PDF class with header and footer."""

    def header(self):
        # Background bar at top
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 28, 'F')

        # Stethoscope emoji workaround - use text symbol
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(129, 92, 246)  # purple
        self.set_xy(10, 7)
        self.cell(0, 14, "HealthBuddy", ln=False)

        self.set_font("Helvetica", "", 9)
        self.set_text_color(148, 163, 184)
        self.set_xy(0, 19)
        self.cell(0, 6, "Comprehensive Health Analysis Report", align="C")

        self.set_text_color(100, 116, 139)
        self.ln(14)

    def footer(self):
        self.set_y(-14)
        self.set_fill_color(15, 23, 42)
        self.rect(0, self.get_y(), 210, 20, 'F')
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f"Page {self.page_no()} | HealthBuddy | For informational purposes only - Not a substitute for professional medical advice", align="C")


def clean_markdown(text: str) -> str:
    """Strip markdown formatting for plain text output."""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*]\s+', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text.strip()


def parse_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    """Parse markdown table lines into headers and rows."""
    headers = []
    rows = []
    for line in lines:
        if not line.strip().startswith('|'):
            continue
        if re.match(r'^\s*\|[\s\-\|:]+\|\s*$', line):
            continue  # separator row
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not headers:
            headers = cells
        else:
            rows.append(cells)
    return headers, rows


def render_section(pdf: FPDF, title: str, emoji: str, content: str, color: tuple):
    """Render a section with a colored header and content."""
    pdf.ln(4)

    # Section header bar
    r, g, b = color
    pdf.set_fill_color(r, g, b)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, pdf_safe_text(f"  {emoji}  {title}"), ln=True, fill=True)
    pdf.ln(2)

    # Parse and render content
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect markdown table block
        if line.strip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[\s\-\|:]+\|\s*$', lines[i + 1]):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            headers, rows = parse_table(table_lines)
            render_table(pdf, headers, rows, color)
            pdf.ln(3)
            continue

        # Heading lines (## or **Title**)
        if line.startswith("##") or (
            line.startswith("**") and line.endswith("**")
        ):
            clean = clean_markdown(line)
            if clean:
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(r, g, b)
                pdf.multi_cell(0, 7, pdf_safe_text(clean))
                pdf.set_text_color(55, 65, 81)
        # Bullet points
        elif line.strip().startswith('- ') or line.strip().startswith('* ') or line.strip().startswith('• '):
            clean = clean_markdown(line)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(55, 65, 81)
            pdf.set_x(14)
            pdf.multi_cell(0, 6, pdf_safe_text(clean))
        # Numbered list
        elif re.match(r'^\d+\.', line.strip()):
            clean = clean_markdown(line)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(55, 65, 81)
            pdf.set_x(14)
            pdf.multi_cell(0, 6, pdf_safe_text(clean))
        # Regular text
        elif line.strip():
            clean = clean_markdown(line)
            if clean:
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(55, 65, 81)
                pdf.multi_cell(0, 6, pdf_safe_text(clean))
        else:
            pdf.ln(2)

        i += 1

    pdf.ln(2)


def render_table(pdf: FPDF, headers: list[str], rows: list[list[str]], color: tuple):
    """Render a markdown table as a styled PDF table."""
    if not headers:
        return

    r, g, b = color
    n_cols = len(headers)
    usable_width = 190
    col_width = usable_width / n_cols

    # Header row
    pdf.set_fill_color(r, g, b)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    for h in headers:
        pdf.cell(col_width, 8, pdf_safe_text(h, 30), border=1, fill=True, align='C')
    pdf.ln()

    # Data rows
    pdf.set_font("Helvetica", "", 9)
    for idx, row in enumerate(rows):
        if idx % 2 == 0:
            pdf.set_fill_color(245, 247, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(30, 41, 59)
        for ci, cell in enumerate(row):
            if ci < n_cols:
                cell_text = pdf_safe_text(clean_markdown(cell), 80)
                pdf.cell(col_width, 7, cell_text, border=1, fill=True)
        # fill missing cells
        for _ in range(n_cols - len(row)):
            pdf.cell(col_width, 7, "", border=1, fill=True)
        pdf.ln()


def generate_pdf_report(results: dict, user_input: str) -> bytes:
    """Generate full PDF report and return as bytes."""
    pdf = HealthcarePDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Meta info box
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(71, 85, 105)
    pdf.ln(2)
    pdf.set_x(10)
    sym = pdf_safe_text(user_input[:120] + ("..." if len(user_input) > 120 else ""))
    pdf.multi_cell(
        0,
        6,
        pdf_safe_text(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}     |     Symptoms: {sym}"
        ),
        border=1,
        fill=True,
    )
    pdf.ln(4)

    # Disclaimer box
    pdf.set_fill_color(255, 251, 235)
    pdf.set_draw_color(245, 158, 11)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(146, 64, 14)
    pdf.set_x(10)
    pdf.multi_cell(
        0,
        6,
        "  DISCLAIMER: This report is for informational/educational purposes only. "
        "Always consult a licensed healthcare professional before making any medical decisions.",
        border="L",
        fill=True,
    )
    pdf.set_draw_color(0, 0, 0)
    pdf.ln(4)

    # Sections config
    sections = [
        ("symptom_analysis",       "Symptom Analysis",              "🧠", (99, 102, 241)),
        ("medication_advice",      "Medication Advice",             "💊", (16, 185, 129)),
        ("home_remedies",          "Home Remedies & Self-Care",     "🌿", (245, 158, 11)),
        ("diet_lifestyle",         "Diet & Lifestyle",              "🥗", (59, 130, 246)),
        ("doctor_recommendations", "Doctor Recommendations",        "👨‍⚕️", (217, 70, 239)),
    ]

    for key, title, emoji, color in sections:
        content = results.get(key, "") or ""
        if content and not str(content).startswith("Error"):
            render_section(pdf, title, emoji, str(content), color)
        elif str(content).startswith("Error"):
            render_section(pdf, title, emoji, "Data unavailable for this section.", color)

    out = pdf.output(dest="S")
    return bytes(out) if isinstance(out, bytearray) else out
