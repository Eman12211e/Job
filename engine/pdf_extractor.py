"""PDF text extraction and cleaning for resume parsing.

Extracts raw text from uploaded PDF resumes using PyMuPDF (fitz),
then cleans common PDF artifacts: broken lines, hyphenated words,
page numbers, headers/footers, and junk characters.
"""

import re
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract all text from a PDF file's bytes.

    Args:
        pdf_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        Concatenated text from all pages, separated by newlines.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)


def clean_pdf_text(raw_text: str) -> str:
    """Clean common PDF extraction artifacts from resume text.

    Handles:
    - Hyphenated words split across lines (e.g., "Soft-\\nware" → "Software")
    - Page numbers and page indicators ("Page 1", "1/3", etc.)
    - Excessive blank lines
    - Leading/trailing whitespace per line
    - Common footer/watermark patterns
    """
    text = raw_text

    # Fix hyphenated words split across lines
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)

    # Remove page numbers: "Page 1", "Page 2 of 5", "1/3", "- 1 -", etc.
    text = re.sub(r"(?i)\bpage\s+\d+(\s+of\s+\d+)?\b", "", text)
    text = re.sub(r"^\s*\d+\s*/\s*\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*-\s*\d+\s*-\s*$", "", text, flags=re.MULTILINE)

    # Remove standalone page numbers (a line that is just a number)
    text = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.MULTILINE)

    # Remove common confidential disclaimers
    text = re.sub(
        r"(?i)\b(confidential|do not distribute|private & confidential)\b.*$",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)

    return text.strip()


def pdf_to_clean_text(pdf_bytes: bytes) -> str:
    """Full pipeline: PDF bytes → extracted text → cleaned text.

    This is the main entry point used by the UI tabs.
    """
    raw = extract_text_from_pdf(pdf_bytes)
    return clean_pdf_text(raw)
