"""
FastAPI Router for Multilingual Voice AI Services
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import base64

from backend.services.voice_service import voice_service, LANG_CONFIGS

router = APIRouter(prefix="/voice", tags=["Voice AI Assistant"])

class ExtractionRequest(BaseModel):
    transcript: str = Field(..., description="Recognized speech transcript text")
    language: str = Field("en", description="Language code (en, hi, gu, mr, te, ta, bn, pa, kn)")
    current_data: Optional[Dict[str, Any]] = Field(default=None, description="Currently populated fields")

class ExtractionResponse(BaseModel):
    extracted_fields: Dict[str, Any]
    missing_fields: List[str]
    followup_question: Optional[str] = None
    confidence: float
    raw_transcript: str

class SynthesisRequest(BaseModel):
    text: str = Field(..., description="Text assessment or prompt to speak aloud")
    language: str = Field("en", description="Target language code")

class SynthesisResponse(BaseModel):
    success: bool
    audio_base64: Optional[str] = None
    mime_type: str = "audio/mp3"
    message: Optional[str] = None

@router.post("/transcribe", summary="Transcribe Spoken Farmer Audio (STT)")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("en")
):
    """
    Transcribes uploaded WAV/MP3/WebM audio using OpenAI Whisper or Google Speech Recognition.
    """
    try:
        content = await file.read()
        res = voice_service.transcribe_audio(content, lang_code=language, filename=file.filename or "audio.wav")
        if not res["success"]:
            raise HTTPException(status_code=400, detail=res.get("error", "Transcription failed"))
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal transcription error: {str(e)}")

@router.post("/extract-entities", response_model=ExtractionResponse, summary="Extract Validated Structured Fields from Transcript")
async def extract_entities(req: ExtractionRequest):
    """
    Extracts validated agronomic fields (crop, acres, district, yield, expenses) from transcript
    and identifies conversational follow-up questions for missing fields.
    """
    try:
        extraction_res = voice_service.extract_agronomic_entities(req.transcript, req.current_data)
        missing = extraction_res["missing_fields"]
        followup = voice_service.get_followup_question(missing, req.language)
        
        return ExtractionResponse(
            extracted_fields=extraction_res["extracted_fields"],
            missing_fields=missing,
            followup_question=followup,
            confidence=extraction_res["confidence"],
            raw_transcript=req.transcript
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity extraction error: {str(e)}")

@router.post("/synthesize", response_model=SynthesisResponse, summary="Synthesize Decision Speech (TTS)")
async def synthesize_speech(req: SynthesisRequest):
    """
    Converts decision assessment text into speech audio bytes (base64) using OpenAI TTS or gTTS.
    """
    try:
        success, audio_bytes, mime = voice_service.synthesize_speech(req.text, req.language)
        if not success or not audio_bytes:
            raise HTTPException(status_code=500, detail="Text-to-speech synthesis failed.")
        
        b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        return SynthesisResponse(
            success=True,
            audio_base64=b64_audio,
            mime_type=mime,
            message="Audio synthesized successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS synthesis error: {str(e)}")

@router.get("/languages", summary="List Supported Multilingual Voice Profiles")
async def list_languages():
    return {
        "supported_languages": LANG_CONFIGS,
        "openai_whisper_available": bool(voice_service.openai_client),
        "google_stt_available": True,
        "gtts_available": True
    }
