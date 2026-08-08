"""
prediction_service.py

Reusable prediction + categorization logic, moved out of the Streamlit
frontend (app.py's `categorize()` function) so both the /predict and
/simulator endpoints share exactly one implementation.
"""
from typing import Dict, List, Tuple

from app.services.model_service import model_service

MAX_TEXT_LENGTH_DEFAULT = 5000


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
    """Runs the ML prediction and attaches category/severity, exactly the
    same way app.py did after calling predict_message()."""
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
