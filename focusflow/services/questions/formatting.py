"""
Question format conversion utilities.
"""
import random
from typing import Dict, List


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
