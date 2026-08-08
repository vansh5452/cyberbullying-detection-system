from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List

from app.services import safety_service

router = APIRouter(prefix="/safety", tags=["Safety"])


@router.get("/tips", summary="Cyber safety coping strategies for students")
def safety_tips():
    return {"success": True, "data": safety_service.SAFETY_TIPS}


@router.get("/helplines", summary="Emergency cyber-crime helplines (India)")
def helplines():
    return {"success": True, "data": safety_service.CYBER_HELPLINES}


@router.get("/laws", summary="Indian cyber law reference (educational only, not legal advice)")
def laws():
    return {
        "success": True,
        "data": safety_service.CYBER_LAWS,
        "disclaimer": "This information is provided for educational purposes only and does "
                       "not constitute personalized legal advice. Consult a qualified legal "
                       "professional or the official helplines for real cases.",
    }


class DetoxRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    matched_words: List[str] = Field(default_factory=list)


@router.post("/detox", summary="Rewrite a toxic message with friendly placeholders")
def detox(payload: DetoxRequest):
    detoxified = safety_service.detoxify_text(payload.text, payload.matched_words)
    highlighted = safety_service.highlight_toxic_words(payload.text, payload.matched_words)
    return {
        "success": True,
        "data": {
            "original_text": payload.text,
            "detoxified_text": detoxified,
            "highlighted_text": highlighted,
        },
    }
