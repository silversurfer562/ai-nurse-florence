# filepath: /Users/patrickroebuck/Documents/pycharm-projects/nurses_api/routers/summarize.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict

from services import summarize_service
from models.schemas import SBARRequest, SBAR
from utils.guardrails import educational_banner

router = APIRouter(prefix="/summarize", tags=["summarize"])


@router.post("/sbar", response_model=SBAR)
def sbar_from_notes(payload: SBARRequest):
    """
    POST /summarize/sbar
    Extract SBAR (Situation, Background, Assessment, Recommendation) from clinical notes.
    """
    sbar_data = summarize_service.sbar_from_notes(payload.notes)
    return SBAR(
        banner=educational_banner(),
        situation=sbar_data.get("situation", ""),
        background=sbar_data.get("background", ""),
        assessment=sbar_data.get("assessment", ""),
        recommendation=sbar_data.get("recommendation", ""),
        references=[]
    )


@router.post("/chat")
async def chat_endpoint(payload: Dict[str, Any]):
    """
    POST /summarize/chat
    Body example: {"prompt": "Summarize this...", "model": "gpt-4o-mini"}
    """
    prompt = payload.get("prompt", "")
    model = payload.get("model", "gpt-4o-mini")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in body")
    try:
        text = summarize_service.call_chatgpt(prompt, model=model)
    except RuntimeError as exc:
        # Surface a 503 when the OpenAI client is not configured or request fails
        raise HTTPException(status_code=503, detail=str(exc))
    return {"text": text}
