"""
Questions service module.
Handles text extraction, question generation, and formatting.
"""
from .extraction import extract_text_from_image, extract_text_from_pdf, extract_text_from_file
from .generation import generate_questions_from_text_lmstudio
from .formatting import _to_app_format

__all__ = [
    'extract_text_from_image',
    'extract_text_from_pdf', 
    'extract_text_from_file',
    'generate_questions_from_text_lmstudio',
    '_to_app_format'
]
