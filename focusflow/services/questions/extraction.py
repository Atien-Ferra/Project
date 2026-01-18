"""
Text extraction functions for various file formats.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_image(file_path: str) -> Optional[str]:
    """
    Extract text from an image using OCR (Tesseract).
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        from PIL import Image
        import pytesseract
        
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return text.strip() if text else None
    except ImportError:
        logger.warning("PIL or pytesseract not installed - image OCR unavailable")
        return None
    except Exception as e:
        logger.error(f"Image text extraction failed: {e}")
        return None


def extract_text_from_pdf(path: str, *, ocr_fallback: bool = True, min_chars: int = 300) -> Optional[str]:
    """
    Extract text from a PDF file.
    
    Strategy:
    1. First try to extract embedded text (fast, works for digital PDFs)
    2. If not enough text found and ocr_fallback=True, use OCR (slower, for scanned PDFs)
    
    Args:
        path: Path to the PDF file
        ocr_fallback: Whether to try OCR if text extraction yields little content
        min_chars: Minimum characters needed before considering OCR fallback
        
    Returns:
        Extracted text or None if extraction fails
    """
    text = ""
    
    # --- Method 1: Text-layer extraction via PyMuPDF ---
    try:
        import pymupdf as fitz
        
        doc = fitz.open(path)
        parts = []
        for page in doc:
            page_text = page.get_text("text") or ""
            parts.append(page_text)
        doc.close()
        text = "\n".join(parts).strip()
        
    except ImportError:
        logger.warning("PyMuPDF not installed - trying alternative PDF extraction")
        # Fallback to PyPDF2 if pymupdf not available
        try:
            import PyPDF2
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                parts = []
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    parts.append(page_text)
                text = "\n".join(parts).strip()
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            text = ""
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        text = ""

    # If we got enough text, return it
    if text and len(text) >= min_chars:
        return text

    # --- Method 2: OCR fallback for scanned PDFs ---
    if not ocr_fallback:
        return text if text else None

    try:
        from pdf2image import convert_from_path
        import pytesseract
        
        logger.info("Attempting OCR fallback for PDF...")
        images = convert_from_path(path, dpi=300)
        ocr_parts = []
        for img in images:
            ocr_parts.append(pytesseract.image_to_string(img))
        ocr_text = "\n".join(ocr_parts).strip()
        
        return ocr_text if ocr_text else (text if text else None)
        
    except ImportError:
        logger.warning("pdf2image or pytesseract not installed - OCR fallback unavailable")
        return text if text else None
    except Exception as e:
        logger.error(f"PDF OCR fallback failed: {e}")
        return text if text else None


def extract_text_from_file(file_path: str, file_type: str) -> Optional[str]:
    """
    Extract text from a file based on its type.
    
    Supported types:
    - pdf: PDF documents (with OCR fallback for scanned docs)
    - docx: Microsoft Word documents
    - txt: Plain text files
    - png, jpg, jpeg: Images (using OCR)
    
    Args:
        file_path: Path to the file
        file_type: File extension (without the dot)
        
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        if file_type == "pdf":
            return extract_text_from_pdf(file_path, ocr_fallback=True)

        elif file_type == "docx":
            from docx import Document
            doc = Document(file_path)
            text = "\n".join(p.text for p in doc.paragraphs)
            return text.strip() if text.strip() else None

        elif file_type == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return text.strip() if text.strip() else None
            
        elif file_type in ("png", "jpg", "jpeg"):
            return extract_text_from_image(file_path)

        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return None
            
    except Exception as e:
        logger.error(f"Text extraction failed for {file_type}: {e}")
        return None
