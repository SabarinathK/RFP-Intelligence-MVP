from datetime import datetime

import fitz

def extract_pdf_text(path: str):
    """Extract FULL text from PDF - no truncation"""
    doc = fitz.open(path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    return "\n".join(pages)


def calculate_days_remaining(deadline):
    """Calculate days until submission deadline"""
    try:
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        return (deadline_date.date() - datetime.utcnow().date()).days
    except Exception:
        return 0
