# focusflow/services/questions.py
import json
import os
import random
import re
from typing import Dict, List, Optional, Tuple
from PIL import Image
import pytesseract
from typing import Optional
import os
from pdf2image import convert_from_path
import pymupdf as fitz

def _normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _extract_json_object(text: str) -> dict:
    """
    Best-effort extraction of a JSON object from a model response.
    """
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])

    raise ValueError("No JSON object found in model output")

def extract_text_from_image(file_path: str) -> str | None:
    try:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)
    except Exception:
        return None

def _to_app_format(raw_questions: List[dict]) -> List[Dict]:
    """
    Convert raw questions:
      {question_text, choices[4], correct_index}
    into your app structure:
      {question_number, question_text, answers[{id,text,is_correct}], correct_answer, category}
    """
    out: List[Dict] = []
    for i, q in enumerate(raw_questions, start=1):
        qt = q["question_text"].strip()
        choices = q["choices"]
        correct_index = int(q["correct_index"])

        answers = []
        for j, choice in enumerate(choices, start=1):
            answers.append(
                {"id": f"q{i}a{j}", "text": str(choice).strip(), "is_correct": (j - 1) == correct_index}
            )

        random.shuffle(answers)
        correct_id = next(a["id"] for a in answers if a["is_correct"])

        out.append(
            {
                "question_number": i,
                "question_text": qt,
                "answers": answers,
                "correct_answer": correct_id,
                "category": "Document-based",
            }
        )
    return out


def extract_text_from_pdf(path: str, *, ocr_fallback: bool = True, min_chars: int = 300) -> Optional[str]:
    """
    1) Try extracting embedded text (fast, best for digital PDFs).
    2) If too little text and ocr_fallback=True, OCR each page (slower, for scanned PDFs).
    """
    # --- 1) Text-layer extraction via PyMuPDF ---
    text = ""
    try:  # PyMuPDF
        doc = fitz.open(path)
        parts = []
        for page in doc:
            # "text" gives readable layout; you can also try "blocks" for more structure
            parts.append(page.get_text("text") or "blocks")
        doc.close() 
        text = "\n".join(parts).strip()
    except Exception:
        text = ""

    if text and len(text) >= min_chars:
        return text

    if not ocr_fallback:
        return text if text else None

    # --- 2) OCR fallback for scanned PDFs ---
    try:
        # If tesseract isn't on PATH in Windows, uncomment and set this:
        # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        images = convert_from_path(path, dpi=300)
        ocr_parts = []
        for img in images:
            ocr_parts.append(pytesseract.image_to_string(img))
        ocr_text = "\n".join(ocr_parts).strip()
        return ocr_text if ocr_text else (text if text else None)
    except Exception:
        # If OCR setup isn't available, return whatever we got from text-layer extraction
        return text if text else None


def extract_text_from_file(file_path: str, file_type: str) -> Optional[str]:
    try:
        if file_type == "pdf":
            return extract_text_from_pdf(file_path, ocr_fallback=True)

        elif file_type == "docx":
            from docx import Document
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs).strip() or None

        elif file_type == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                t = f.read()
            return t.strip() or None
        elif file_type in ("png", "jpg", "jpeg"):
            return extract_text_from_image(file_path)

        return None
    except Exception:
        return None


def generate_questions_from_text_lmstudio(text: str, num_questions: int = 5) -> Optional[List[Dict]]:
    if not text or not text.strip():
        return None

    from openai import OpenAI  # imported here so project still runs without openai if you want fallback

    base_url = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:5500/")
    model_id = os.getenv("LMSTUDIO_MODEL_ID", "openai/gpt-oss-20b")

    client = OpenAI(base_url=base_url, api_key="lm-studio")

    excerpt = _normalize_ws(text)[:12000]

    prompt = f"""
Create {num_questions} multiple-choice questions from the text below.

Rules:
- Exactly 4 choices per question
- Exactly 1 correct choice
- Answers must be supported by the text (no outside info) and no hallucinations
- Keep wording clear and not tricky
Return ONLY valid JSON in this exact shape:

{{
  "questions": [
    {{
      "question_text": "...",
      "choices": ["A", "B", "C", "D"],
      "correct_index": 0
    }}
  ]
}}

TEXT:
{excerpt}
""".strip()

    completion = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You generate high-quality MCQs strictly grounded in the given text."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    content = completion.choices[0].message.content or ""
    data = _extract_json_object(content)

    raw_questions = data.get("questions", [])
    if not isinstance(raw_questions, list) or len(raw_questions) < 1:
        return None

    # Truncate to requested number and validate enough content
    raw_questions = raw_questions[:num_questions]
    for q in raw_questions:
        if not all(k in q for k in ("question_text", "choices", "correct_index")):
            return None
        if not isinstance(q["choices"], list) or len(q["choices"]) != 4:
            return None

    return _to_app_format(raw_questions)

