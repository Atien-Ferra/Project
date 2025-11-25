# focusflow/services/questions.py
import json
import os
import random
import re
from typing import Dict, List, Optional, Tuple


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


def generate_questions_from_text_lmstudio(text: str, num_questions: int = 5) -> Optional[List[Dict]]:
    if not text or not text.strip():
        return None

    from openai import OpenAI  # imported here so project still runs without openai if you want fallback

    base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
    model_id = os.getenv("LMSTUDIO_MODEL_ID", "openai/gpt-oss-20b")

    client = OpenAI(base_url=base_url, api_key="lm-studio")

    excerpt = _normalize_ws(text)[:12000]

    prompt = f"""
Create {num_questions} multiple-choice questions from the text below.

Rules:
- Exactly 4 choices per question
- Exactly 1 correct choice
- Answers must be supported by the text (no outside info)
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

