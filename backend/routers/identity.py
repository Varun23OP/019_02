from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from backend.database import get_db
from backend.models import Farmer, CreditAssessment, CropVerification
from backend.schemas import ConsentRecordRequest
from backend.services.identity_blockchain import FarmerIdentityService
from backend.services.gdpr_consent import GDPRConsentService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/farmer/{farmer_id}/credential")
async def get_farmer_verifiable_credential(farmer_id: int, db: Session = Depends(get_db)):
    """
    Export portable W3C Verifiable Credential for farmer.
    Can be imported by any participating rural bank without land titles.
    """
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found")

    assessment = db.query(CreditAssessment).filter(
        CreditAssessment.farmer_id == farmer_id
    ).order_by(CreditAssessment.id.desc()).first()

    credit_score = assessment.credit_score if assessment else 80
    credit_limit = assessment.loan_eligibility_amount if assessment else 25000.0
    crop = assessment.crop_name if assessment else "Tomato (Horticulture)"
    acres = assessment.acres if assessment else farmer.land_size_acres
    due_date = assessment.bullet_repayment_date.strftime("%Y-%m-%d") if assessment and assessment.bullet_repayment_date else "2027-01-15"

    vc = FarmerIdentityService.issue_verifiable_credit_credential(
        farmer_id=farmer.id,
        farmer_name=farmer.name,
        phone=farmer.phone,
        state=farmer.state,
        crop_name=crop,
        acres=acres,
        credit_score=credit_score,
        credit_limit=credit_limit,
        bullet_due_date=due_date,
        peer_guarantors=["Peer Guarantor 1", "Peer Guarantor 2", "Peer Guarantor 3"],
        fpo_name="Sahyadri Agro Producer Co."
    )
    return vc


@router.post("/verify-credential")
async def verify_credential_authenticity(credential_doc: Dict[str, Any]):
    """
    Cryptographically verify the authenticity and tamper status of a portable credential.
    """
    return FarmerIdentityService.verify_credential_document(credential_doc)


@router.post("/consent")
async def record_farmer_consent(request: ConsentRecordRequest):
    """
    Capture explicit, granular consent audit trail conforming to GDPR and DPDP regulations.
    """
    return GDPRConsentService.create_consent_record(
        farmer_id=request.farmer_id,
        consent_credit_assessment=request.consent_credit_assessment,
        consent_fpo_sharing=request.consent_fpo_sharing,
        consent_mandi_alerts=request.consent_mandi_alerts
    )


@router.get("/gdpr/export/{farmer_id}")
async def export_gdpr_dossier(farmer_id: int, db: Session = Depends(get_db)):
    """
    GDPR Article 15/20: Export complete personal data and credit dossier in JSON.
    """
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found")

    assessments = db.query(CreditAssessment).filter(CreditAssessment.farmer_id == farmer_id).all()
    verifications = db.query(CropVerification).filter(CropVerification.farmer_id == farmer_id).all()

    return GDPRConsentService.export_data_subject_dossier(
        farmer_obj=farmer,
        assessments=[{"id": a.id, "score": a.credit_score, "limit": a.loan_eligibility_amount, "date": str(a.assessment_date)} for a in assessments],
        verifications=[{"crop": v.crop_name, "stage": v.crop_stage, "status": v.verification_status} for v in verifications]
    )


@router.delete("/gdpr/forget/{farmer_id}")
async def anonymize_farmer(farmer_id: int, db: Session = Depends(get_db)):
    """
    GDPR Article 17: Right to Erasure / Anonymization of personal identifying information.
    """
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found")

    anonymized = GDPRConsentService.anonymize_farmer_record(farmer)
    farmer.name = anonymized["name"]
    farmer.phone = anonymized["phone"]
    farmer.village = anonymized["village"]
    farmer.status = "inactive"
    db.commit()

    return {
        "status": "ANONYMIZATION_COMPLETED",
        "farmer_id": farmer_id,
        "message": "Personal identifying information anonymized in accordance with GDPR Article 17."
    }
