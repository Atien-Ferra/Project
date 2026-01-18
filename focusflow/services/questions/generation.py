"""
LM Studio question generation.
"""
import json
import os
import re
import logging
from typing import Dict, List, Optional
from .formatting import _to_app_format

logger = logging.getLogger(__name__)


def _normalize_ws(s: str) -> str:
    """
    Normalize whitespace in a string.
    Replaces multiple spaces/newlines with single spaces.
    """
    return re.sub(r"\s+", " ", s).strip()


def _extract_json_object(text: str) -> dict:
    """
    Extract a JSON object from LLM response text.
    LLMs sometimes include extra text before/after the JSON,
    so we need to find and extract just the JSON part.
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
