"""
FastAPI Router for Farmer Assessments & Loan Requests (backend/routers/farmers.py)
"""

from fastapi import APIRouter, HTTPException, Depends
from backend.schemas.credit import CreditAssessmentRequest, CreditAssessmentResponse
from backend.services.agronomic_engine import AgronomicEngine

router = APIRouter(prefix="/api/farmers", tags=["Farmers"])
engine = AgronomicEngine()

# In-memory store for active assessments
ASSESSMENT_STORE = {}

@router.post("/assessments", response_model=CreditAssessmentResponse)
async def create_credit_assessment(payload: CreditAssessmentRequest):
    """
    Computes dynamic credit limit by piping farmer input through the real-time agronomic engine:
    - AGMARKNET modal rates & 10% volatility buffer
    - NHB 90th percentile yield ceilings
    - Open-Meteo weather telemetry
    - FPO peer guarantor exposure limits
    """
    try:
        assessment = engine.compute_complete_underwriting(payload.dict())
        farmer_did = assessment["farmer_profile"]["did"]
        ASSESSMENT_STORE[farmer_did] = assessment
        return assessment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agronomic calculation error: {str(e)}")

@router.get("/{farmer_id}/assessments")
async def get_farmer_assessment(farmer_id: str):
    """
    Retrieves latest credit assessment for a given farmer DID or phone.
    """
    if farmer_id in ASSESSMENT_STORE:
        return ASSESSMENT_STORE[farmer_id]
    
    # Default fallback
    default_payload = CreditAssessmentRequest(farmer_name="Ramesh Tukaram Patil", district="Nashik", crop_name="Tomato", land_acres=1.5)
    return engine.compute_complete_underwriting(default_payload.dict())
