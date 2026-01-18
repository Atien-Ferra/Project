"""
Files service module.
Handles file validation and text extraction.
"""
from .handlers import allowed_file, extract_text_from_file, ALLOWED_EXTENSIONS

__all__ = ['allowed_file', 'extract_text_from_file', 'ALLOWED_EXTENSIONS']
