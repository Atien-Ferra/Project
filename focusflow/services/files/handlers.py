"""
File handling utilities.
"""
from typing import Optional

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "png", "jpg", "jpeg"}


def allowed_file(filename: str) -> bool:
    """Check if a file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(file_path: str, file_type: str) -> Optional[str]:
    """Extract text content from a file based on its type."""
    try:
        if file_type == "pdf":
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    t = page.extract_text() or ""
                    text += t
                return text

        if file_type == "docx":
            from docx import Document
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)

        if file_type == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        return None
    except Exception:
        return None
