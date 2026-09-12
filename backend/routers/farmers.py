"""
FastAPI Router for Farmer Profiles, Assessments & Underwriting Sync (backend/routers/farmers.py)
Supports SQLite ORM persistence and agronomic assessment caching.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from backend.database import get_db
from backend.models import Farmer, CreditAssessment, FarmerStatus
from backend.schemas import (
    FarmerCreate,
    FarmerUpdate,
    FarmerResponse,
    CreditAssessmentCreate,
    CreditAssessmentResponse
)
from backend.schemas.credit import CreditAssessmentRequest, CreditAssessmentResponse as EngineCreditAssessmentResponse
from backend.services.agronomic_engine import AgronomicEngine

router = APIRouter()
logger = logging.getLogger(__name__)
engine = AgronomicEngine()

# In-memory cache for fast active assessments
ASSESSMENT_STORE: Dict[str, Any] = {}


@router.post("/", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
async def create_farmer(farmer: FarmerCreate, db: Session = Depends(get_db)):
    """Create a new farmer or return existing if phone matches"""
    try:
        existing_farmer = db.query(Farmer).filter(Farmer.phone == farmer.phone).first()
        if existing_farmer:
            existing_farmer.name = farmer.name
            existing_farmer.land_size_acres = farmer.get_land_size()
            if farmer.village:
                existing_farmer.village = farmer.village
            if farmer.district:
                existing_farmer.district = farmer.district
            if farmer.state:
                existing_farmer.state = farmer.state
            db.commit()
            db.refresh(existing_farmer)
            return existing_farmer
        
        db_farmer = Farmer(
            name=farmer.name,
            phone=farmer.phone,
            village=farmer.village or "Pimpalgaon",
            district=farmer.district or "Nashik",
            state=farmer.state or "Maharashtra",
            land_size_acres=farmer.get_land_size(),
            status=FarmerStatus.ACTIVE
        )
        db.add(db_farmer)
        db.commit()
        db.refresh(db_farmer)
        logger.info(f"Created farmer: {db_farmer.id}")
        return db_farmer
    except Exception as e:
        logger.error(f"Error creating farmer: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create farmer: {str(e)}"
        )


@router.get("/", response_model=List[FarmerResponse])
async def get_farmers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all farmers with pagination"""
    try:
        farmers = db.query(Farmer).offset(skip).limit(limit).all()
        return farmers
    except Exception as e:
        logger.error(f"Error fetching farmers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch farmers"
        )


@router.get("/{farmer_id}", response_model=FarmerResponse)
async def get_farmer(farmer_id: int, db: Session = Depends(get_db)):
    """Get a specific farmer by ID"""
    try:
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer not found"
            )
        return farmer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching farmer {farmer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch farmer"
        )


@router.put("/{farmer_id}", response_model=FarmerResponse)
async def update_farmer(farmer_id: int, farmer_update: FarmerUpdate, db: Session = Depends(get_db)):
    """Update a farmer"""
    try:
        db_farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not db_farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer not found"
            )
        
        update_data = farmer_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_farmer, field, value)
        
        db.commit()
        db.refresh(db_farmer)
        logger.info(f"Updated farmer: {farmer_id}")
        return db_farmer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating farmer {farmer_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update farmer"
        )


@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farmer(farmer_id: int, db: Session = Depends(get_db)):
    """Delete a farmer"""
    try:
        db_farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not db_farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer not found"
            )
        
        db.delete(db_farmer)
        db.commit()
        logger.info(f"Deleted farmer: {farmer_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting farmer {farmer_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete farmer"
        )


@router.post("/{farmer_id}/assessments", response_model=CreditAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_credit_assessment(farmer_id: int, assessment: CreditAssessmentCreate, db: Session = Depends(get_db)):
    """Create a credit assessment for a farmer in SQLite database"""
    try:
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer not found"
            )
        
        assessment_data = assessment.model_dump()
        assessment_data['farmer_id'] = farmer_id
        
        db_assessment = CreditAssessment(**assessment_data)
        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)
        logger.info(f"Created credit assessment for farmer: {farmer_id}")
        return db_assessment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating credit assessment: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create credit assessment"
        )


@router.get("/{farmer_id}/assessments", response_model=List[CreditAssessmentResponse])
async def get_farmer_assessments(farmer_id: int, db: Session = Depends(get_db)):
    """Get all credit assessments for a farmer from SQLite database"""
    try:
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer not found"
            )
        
        assessments = db.query(CreditAssessment).filter(
            CreditAssessment.farmer_id == farmer_id
        ).all()
        return assessments
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assessments for farmer {farmer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch credit assessments"
        )


# Legacy Agronomic Engine Endpoint Compatibility
@router.post("/engine/assessments", response_model=EngineCreditAssessmentResponse)
async def create_engine_credit_assessment(payload: CreditAssessmentRequest):
    """Compute dynamic credit limit via legacy AgronomicEngine"""
    try:
        assessment = engine.compute_complete_underwriting(payload.dict())
        farmer_did = assessment["farmer_profile"]["did"]
        ASSESSMENT_STORE[farmer_did] = assessment
        return assessment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agronomic calculation error: {str(e)}")
