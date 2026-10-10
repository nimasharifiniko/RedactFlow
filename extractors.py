import os
import pdfplumber
from docx import Document


def extract_from_pdf(filepath):
    text_parts = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_from_docx(filepath):
    doc = Document(filepath)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])


def extract_from_txt(filepath):
    # استفاده از utf-8-sig باعث میشه بایت‌های BOM ویندوز خودکار حذف بشن
    with open(filepath, "r", encoding="utf-8-sig", errors="ignore") as f:
        return f.read()


def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return extract_from_pdf(filepath)
    elif ext == ".docx":
        return extract_from_docx(filepath)
    elif ext == ".txt":
        return extract_from_txt(filepath)
    else:
        raise ValueError(f"file type not supported: {ext}")
