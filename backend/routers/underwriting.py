from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime

from backend.database import get_db
from backend.models import Farmer, CreditAssessment, FarmerStatus
from backend.schemas import UnderwritingCalculateRequest
from backend.services.underwriting import UnderwritingService
from backend.services.identity_blockchain import FarmerIdentityService
from backend.services.agri_data import AgriDataService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/calculate", response_model=Dict[str, Any])
async def calculate_underwriting(request: UnderwritingCalculateRequest):
    """
    Execute real-time agronomic underwriting calculation.
    Deterministic, transparent, sub-second execution (< 50ms).
    """
    try:
        assessment = UnderwritingService.calculate_assessment(
            farmer_name=request.farmer_name,
            phone=request.phone,
            crop_name=request.crop_name,
            acres=request.acres,
            projected_yield=request.projected_yield,
            seeds_cost=request.seeds_cost,
            fertilizer_cost=request.fertilizer_cost,
            labour_cost=request.labour_cost,
            irrigation_other_cost=request.irrigation_other_cost,
            peer_guarantors_count=request.peer_guarantors_count,
            is_consistent_performer=request.is_consistent_performer,
            custom_price=request.custom_price
        )
        return assessment
    except Exception as e:
        logger.error(f"Error in underwriting calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Underwriting calculation failed: {str(e)}"
        )


@router.post("/submit-application", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def submit_underwriting_application(
    request: UnderwritingCalculateRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate underwriting, upsert farmer profile, and persist CreditAssessment to SQLite.
    Also issues a portable W3C Verifiable Credential.
    """
    try:
        # 1. Execute deterministic underwriting
        result = UnderwritingService.calculate_assessment(
            farmer_name=request.farmer_name,
            phone=request.phone,
            crop_name=request.crop_name,
            acres=request.acres,
            projected_yield=request.projected_yield,
            seeds_cost=request.seeds_cost,
            fertilizer_cost=request.fertilizer_cost,
            labour_cost=request.labour_cost,
            irrigation_other_cost=request.irrigation_other_cost,
            peer_guarantors_count=request.peer_guarantors_count,
            is_consistent_performer=request.is_consistent_performer,
            custom_price=request.custom_price
        )

        # 2. Upsert Farmer
        farmer = db.query(Farmer).filter(Farmer.phone == request.phone).first()
        if not farmer:
            farmer = Farmer(
                name=request.farmer_name,
                phone=request.phone,
                village="Pimpalgaon",
                district="Nashik",
                state="Maharashtra",
                land_size_acres=request.acres,
                status=FarmerStatus.ACTIVE
            )
            db.add(farmer)
            db.commit()
            db.refresh(farmer)
        else:
            farmer.name = request.farmer_name
            farmer.land_size_acres = request.acres
            db.commit()

        # Parse bullet repayment date
        bullet_date = datetime.strptime(
            result["amortization"]["bullet_due_date"], "%Y-%m-%d"
        )

        # 3. Save Credit Assessment record
        db_assessment = CreditAssessment(
            farmer_id=farmer.id,
            assessment_date=datetime.utcnow(),
            credit_score=result["credit_score"],
            loan_eligibility_amount=result["credit_limit"],
            risk_category=result["risk_category"],
            crop_name=request.crop_name,
            acres=request.acres,
            projected_yield=request.projected_yield,
            mandi_price_per_qtl=result["mandi_price_per_qtl"],
            gross_revenue=result["gross_revenue"],
            total_expenses=result["expenses_breakdown"]["total"],
            net_profit=result["net_profit"],
            pmfby_insured=result["pmfby_insured"],
            bullet_repayment_date=bullet_date,
            status="PENDING_REVIEW",
            score_breakdown=json.dumps(result["score_factors"]),
            notes=result["explanation"]["en"]
        )
        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)

        # 4. Generate portable W3C Verifiable Credential
        vc = FarmerIdentityService.issue_verifiable_credit_credential(
            farmer_id=farmer.id,
            farmer_name=farmer.name,
            phone=farmer.phone,
            state=farmer.state,
            crop_name=request.crop_name,
            acres=request.acres,
            credit_score=result["credit_score"],
            credit_limit=result["credit_limit"],
            bullet_due_date=result["amortization"]["bullet_due_date"],
            peer_guarantors=["Peer Guarantor 1", "Peer Guarantor 2", "Peer Guarantor 3"],
            fpo_name="Sahyadri Agro Producer Co."
        )

        # 5. Mandi & Harvest alerts
        alerts = AgriDataService.generate_alerts(request.crop_name, request.acres, bullet_date)

        return {
            "farmer_id": farmer.id,
            "assessment_id": db_assessment.id,
            "underwriting_result": result,
            "verifiable_credential": vc,
            "proactive_alerts": alerts,
            "status": "ASSESSMENT_PERSISTED_READY_FOR_LENDER"
        }
    except Exception as e:
        logger.error(f"Error submitting underwriting application: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit application: {str(e)}"
        )


@router.get("/farmer/{farmer_id}/latest")
async def get_latest_farmer_assessment(farmer_id: int, db: Session = Depends(get_db)):
    """Retrieve the most recent agronomic underwriting assessment for a farmer."""
    assessment = db.query(CreditAssessment).filter(
        CreditAssessment.farmer_id == farmer_id
    ).order_by(CreditAssessment.id.desc()).first()

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assessment found for this farmer"
        )
    
    return assessment
