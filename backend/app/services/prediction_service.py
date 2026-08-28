"""
prediction_service.py

Reusable prediction + categorization logic, moved out of the Streamlit
frontend (app.py's `categorize()` function) so both the /predict and
/simulator endpoints share exactly one implementation.
"""
from typing import Dict, List, Optional, Tuple
import json
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.services.model_service import model_service

MAX_TEXT_LENGTH_DEFAULT = 5000


def predict_with_gemini(text: str) -> Optional[Dict]:
    """Calls Gemini API using standard HTTP REST interface to classify text.
    Returns structured dict matching build_prediction_response, or None on failure."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None

    # Use gemini-1.5-flash which is widely available, fast, and has generous free limits
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    prompt = (
        "You are an expert safety classifier. Analyze the following message for cyberbullying, toxicity, "
        "harassment, hate speech, threats, or abuse.\n"
        "Return a JSON object containing:\n"
        '- "is_cyberbullying": boolean (true if the text contains cyberbullying, hate speech, harassment, threats, or insults)\n'
        '- "confidence": number (between 0.0 and 1.0, representing your classification confidence)\n'
        '- "category": string (must be exactly one of: "Insult / Name-calling", "Threat / Intimidation", "Hate Speech / Discrimination", "Sexual Harassment", "Not Applicable")\n'
        '- "severity": string (must be exactly one of: "High", "Medium-High", "Medium", "None")\n'
        '- "matched_words": list of strings (specific vulgar or abusive words detected from the text)\n\n'
        f"Text to analyze: {text}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "is_cyberbullying": {"type": "BOOLEAN"},
                    "confidence": {"type": "NUMBER"},
                    "category": {"type": "STRING"},
                    "severity": {"type": "STRING"},
                    "matched_words": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    }
                },
                "required": ["is_cyberbullying", "confidence", "category", "severity", "matched_words"]
            }
        }
    }

    try:
        resp = httpx.post(url, json=payload, timeout=10.0)
        if resp.status_code != 200:
            logger.error(f"Gemini API returned error code {resp.status_code}: {resp.text}")
            return None

        response_data = resp.json()
        candidate = response_data.get("candidates", [{}])[0]
        text_response = candidate.get("content", {}).get("parts", [{}])[0].get("text", "").strip()

        if not text_response:
            return None

        result = json.loads(text_response)

        is_bullying = bool(result.get("is_cyberbullying"))
        return {
            "label": 1 if is_bullying else 0,
            "confidence": float(result.get("confidence", 0.95)),
            "matched_words": list(result.get("matched_words", [])),
            "method": "Gemini 1.5 Flash",
            "category": str(result.get("category", "Not Applicable")),
            "severity": str(result.get("severity", "None")),
        }
    except Exception as e:
        logger.error(f"Gemini API request failed: {e}")
        return None


def categorize_prediction(cleaned_text: str, matched_words: List[str]) -> Tuple[str, str]:
    """Identical to the original app.py `categorize()` function."""
    if any(t in cleaned_text for t in
           ['kill', 'destroy', 'beat', 'leak', 'hunt you', 'ruin your life', 'watch your back', 'pay for']):
        return "Threat / Intimidation", "High"
    elif any(h in cleaned_text for h in
             ['country', 'race', 'religion', 'inferior', 'belong', 'disease', 'village']):
        return "Hate Speech / Discrimination", "Medium-High"
    else:
        return "Insult / Name-calling", "Medium"


def predict_text(text: str) -> Dict:
    """Runs the prediction using Gemini if configured, otherwise falls back
    to the offline ML (TF-IDF + Logistic Regression) classifier."""
    # Attempt to predict with Gemini first
    gemini_result = predict_with_gemini(text)
    if gemini_result is not None:
        return gemini_result

    # Fallback to local ML model pipeline
    result = model_service.predict(text)
    cleaned = model_service.clean_text(text)

    category, severity = ("Not Applicable", "None")
    if result['label'] == 1:
        category, severity = categorize_prediction(cleaned, result['matched_words'])

    result['category'] = category
    result['severity'] = severity
    return result


def build_prediction_response(result: Dict) -> Dict:
    """Shapes a predict_text() result into the API's documented response schema."""
    is_bullying = result['label'] == 1
    confidence = float(result['confidence'])
    return {
        "label": result['label'],
        "is_cyberbullying": is_bullying,
        "prediction": "Cyberbullying" if is_bullying else "Safe",
        "confidence": confidence,
        "confidence_percent": round(confidence * 100, 2),
        "matched_words": result['matched_words'],
        "method": result['method'],
        "category": result['category'],
        "severity": result['severity'],
    }
