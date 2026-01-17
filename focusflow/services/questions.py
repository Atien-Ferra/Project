"""
Question Generation Service
===========================
This module handles:
1. Text extraction from various file formats (PDF, DOCX, TXT, images)
2. Question generation using LM Studio's local LLM API
3. Conversion of raw LLM output to the app's question format

LM Studio Setup:
- Make sure LM Studio is running with a model loaded
- Set LMSTUDIO_BASE_URL in .env (default: http://127.0.0.1:1234/v1)
- Set LMSTUDIO_MODEL_ID in .env (or leave blank for auto-detection)
"""

import json
import os
import random
import re
import logging
from typing import Dict, List, Optional

# Set up logging for debugging
logger = logging.getLogger(__name__)

# ============================================
# UTILITY FUNCTIONS
# ============================================

def _normalize_ws(s: str) -> str:
    """
    Normalize whitespace in a string.
    Replaces multiple spaces/newlines with single spaces.
    
    Args:
        s: Input string
        
    Returns:
        String with normalized whitespace
    """
    return re.sub(r"\s+", " ", s).strip()


def _extract_json_object(text: str) -> dict:
    """
    Extract a JSON object from LLM response text.
    LLMs sometimes include extra text before/after the JSON,
    so we need to find and extract just the JSON part.
    
    Args:
        text: Raw text from LLM response
        
    Returns:
        Parsed JSON as a dictionary
        
    Raises:
        ValueError: If no valid JSON object found
    """
    text = text.strip()
    
    # If text is already clean JSON, parse directly
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON object boundaries
    start = text.find("{")
    end = text.rfind("}")
    
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Attempted to parse: {text[start:end+1][:500]}...")
    
    raise ValueError("No valid JSON object found in model output")


# ============================================
# TEXT EXTRACTION FUNCTIONS
# ============================================

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


# ============================================
# QUESTION FORMAT CONVERSION
# ============================================

def _to_app_format(raw_questions: List[dict]) -> List[Dict]:
    """
    Convert raw LLM questions to the app's expected format.
    
    Input format (from LLM):
    {
        "question_text": "...",
        "choices": ["A", "B", "C", "D"],
        "correct_index": 0  # 0-based index
    }
    
    Output format (for app):
    {
        "question_number": 1,
        "question_text": "...",
        "answers": [
            {"id": "q1a1", "text": "A", "is_correct": True},
            {"id": "q1a2", "text": "B", "is_correct": False},
            ...
        ],
        "correct_answer": "q1a1",  # ID of correct answer
        "category": "Document-based"
    }
    
    Args:
        raw_questions: List of questions in LLM format
        
    Returns:
        List of questions in app format
    """
    out: List[Dict] = []
    
    for i, q in enumerate(raw_questions, start=1):
        question_text = q["question_text"].strip()
        choices = q["choices"]
        correct_index = int(q["correct_index"])

        # Build answers list with unique IDs
        answers = []
        for j, choice in enumerate(choices, start=1):
            answers.append({
                "id": f"q{i}a{j}",
                "text": str(choice).strip(),
                "is_correct": (j - 1) == correct_index  # j is 1-based, correct_index is 0-based
            })

        # Shuffle answers so correct answer isn't always first
        random.shuffle(answers)
        
        # Find the ID of the correct answer after shuffling
        correct_id = next(a["id"] for a in answers if a["is_correct"])

        out.append({
            "question_number": i,
            "question_text": question_text,
            "answers": answers,
            "correct_answer": correct_id,
            "category": "Document-based",
        })
        
    return out


# ============================================
# LM STUDIO QUESTION GENERATION
# ============================================

def generate_questions_from_text_lmstudio(text: str, num_questions: int = 5) -> Optional[List[Dict]]:
    """
    Generate multiple-choice questions from text using LM Studio's API.
    
    This function:
    1. Connects to your local LM Studio server
    2. Sends the document text with a prompt
    3. Parses the JSON response containing questions
    4. Converts to the app's expected format
    
    Environment Variables:
    - LMSTUDIO_BASE_URL: Base URL for LM Studio API (default: http://127.0.0.1:1234/v1)
    - LMSTUDIO_MODEL_ID: Model identifier (optional, uses loaded model if not set)
    
    Args:
        text: Document text to generate questions from
        num_questions: Number of questions to generate (default: 5)
        
    Returns:
        List of questions in app format, or None if generation fails
    """
    # Validate input
    if not text or not text.strip():
        logger.warning("Empty text provided for question generation")
        return None

    # Import OpenAI client (used for LM Studio's OpenAI-compatible API)
    try:
        from openai import OpenAI
    except ImportError:
        logger.error("openai package not installed - run: pip install openai")
        return None

    # Get LM Studio configuration from environment
    # Default port 1234 is LM Studio's default
    base_url = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
    model_id = os.getenv("LMSTUDIO_MODEL_ID", "")  # Empty string = use currently loaded model
    
    logger.info(f"Connecting to LM Studio at {base_url}")
    
    # Create OpenAI client configured for LM Studio
    # api_key is required but ignored by LM Studio
    client = OpenAI(
        base_url=base_url,
        api_key="lm-studio"  # LM Studio ignores this but OpenAI client requires it
    )

    # Truncate text to avoid token limits (most models have 4K-8K context)
    # 12000 chars ≈ 3000 tokens, leaving room for prompt and response
    excerpt = _normalize_ws(text)[:12000]

    # Build the prompt for question generation
    prompt = f"""Create {num_questions} multiple-choice questions based on the following text.

RULES:
- Each question must have exactly 4 choices
- Exactly 1 choice must be correct
- Questions must be answerable using ONLY the provided text
- Do not use information from outside the text
- Keep questions clear and not tricky

Return ONLY valid JSON in this exact format (no other text):

{{
  "questions": [
    {{
      "question_text": "Your question here?",
      "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
      "correct_index": 0
    }}
  ]
}}

TEXT TO CREATE QUESTIONS FROM:
{excerpt}
""".strip()

    try:
        # Make the API call to LM Studio
        logger.info(f"Sending request to LM Studio (model: {model_id or 'default'})...")
        
        completion = client.chat.completions.create(
            model=model_id if model_id else "local-model",  # LM Studio uses loaded model
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates high-quality multiple-choice questions. You always respond with valid JSON only, no additional text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent output
            max_tokens=2000,  # Enough for 5 questions
        )

        # Extract response content
        content = completion.choices[0].message.content or ""
        logger.debug(f"LM Studio response: {content[:500]}...")
        
        # Parse JSON from response
        data = _extract_json_object(content)
        
        # Validate response structure
        raw_questions = data.get("questions", [])
        if not isinstance(raw_questions, list) or len(raw_questions) < 1:
            logger.error("No questions found in LM Studio response")
            return None

        # Truncate to requested number
        raw_questions = raw_questions[:num_questions]
        
        # Validate each question
        for idx, q in enumerate(raw_questions):
            # Check required fields exist
            if not all(k in q for k in ("question_text", "choices", "correct_index")):
                logger.error(f"Question {idx+1} missing required fields")
                return None
            
            # Check choices is a list of 4 items
            if not isinstance(q["choices"], list) or len(q["choices"]) != 4:
                logger.error(f"Question {idx+1} doesn't have exactly 4 choices")
                return None
            
            # Validate correct_index is in range
            if not isinstance(q["correct_index"], int) or q["correct_index"] < 0 or q["correct_index"] > 3:
                logger.error(f"Question {idx+1} has invalid correct_index")
                return None

        # Convert to app format and return
        logger.info(f"Successfully generated {len(raw_questions)} questions")
        return _to_app_format(raw_questions)
        
    except ConnectionError as e:
        logger.error(f"Cannot connect to LM Studio at {base_url}. Is it running?")
        logger.error(f"Error: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Question generation failed: {e}")
        logger.exception("Full traceback:")
        return None
