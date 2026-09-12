from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Dict, Any, Optional
import logging

from backend.services.voice_nlp import VoiceNLPService, SUPPORTED_LANGUAGES
from backend.schemas import VoiceParseRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/languages")
async def get_supported_languages():
    """List all 10+ supported Indian languages for voice-based credit intake."""
    return {
        "supported_languages_count": len(SUPPORTED_LANGUAGES),
        "languages": SUPPORTED_LANGUAGES
    }


@router.get("/sample/{lang_code}")
async def get_sample_vernacular_voice(lang_code: str = "hi"):
    """
    Get a pre-loaded authentic vernacular utterance and mapped fields
    for 1-click demonstration across 11 languages.
    """
    sample = VoiceNLPService.get_sample_utterance(lang_code)
    return {
        "lang_code": lang_code,
        "sample_data": sample
    }


@router.post("/parse")
async def parse_spoken_transcript(request: VoiceParseRequest):
    """
    Map spoken/typed transcript to structured form fields.
    Enables review and correction by farmer before underwriting.
    """
    try:
        parsed = VoiceNLPService.parse_transcript_to_fields(
            transcript=request.transcript,
            lang_code=request.lang_code,
            current_data=request.current_data
        )
        return parsed
    except Exception as e:
        logger.error(f"Error parsing voice transcript: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract entities: {str(e)}"
        )


@router.post("/transcribe-audio")
async def transcribe_audio_file(
    file: UploadFile = File(...),
    lang_code: str = Form("hi")
):
    """
    Accept real recorded audio file (WAV/MP3/WEBM), transcribe speech,
    and map into form fields for farmer review.
    """
    try:
        content = await file.read()
        transcription_res = VoiceNLPService.transcribe_audio_bytes(content, lang_code)
        if transcription_res.get("success") and transcription_res.get("raw_transcript"):
            parsed_fields = VoiceNLPService.parse_transcript_to_fields(
                transcript=transcription_res["raw_transcript"],
                lang_code=lang_code
            )
        else:
            parsed_fields = {
                "mapped_fields": {},
                "extracted_fields": {},
                "proposed_changes": {},
                "confidence_scores": {},
                "missing_fields": ["crop", "acres", "district", "yield", "costs"],
                "clarifications": [transcription_res.get("error", "Speech could not be understood.")],
                "contradictions": [],
                "raw_transcript": "",
                "requires_review": True
            }
        return {
            "file_name": file.filename,
            "transcription": transcription_res,
            "parsed_fields": parsed_fields,
            "can_review_and_edit": True
        }
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio transcription failed: {str(e)}"
        )

