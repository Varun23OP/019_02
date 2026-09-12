from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.models import FarmerStatus


class FarmerBase(BaseModel):
    """Base schema for Farmer"""
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    village: Optional[str] = Field("Pimpalgaon", max_length=255)
    district: Optional[str] = Field("Nashik", max_length=255)
    state: Optional[str] = Field("Maharashtra", max_length=255)
    land_size_acres: float = Field(..., gt=0, le=10.0)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format"""
        clean = v.replace('+', '').replace('-', '').replace(' ', '')
        if not clean.isdigit():
            raise ValueError('Phone number must contain only digits, +, -, and spaces')
        return v


class FarmerCreate(BaseModel):
    """Schema for creating a farmer, accepting flexible alias fields"""
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    village: Optional[str] = Field("Pimpalgaon", max_length=255)
    district: Optional[str] = Field("Nashik", max_length=255)
    state: Optional[str] = Field("Maharashtra", max_length=255)
    land_size_acres: Optional[float] = Field(None, gt=0, le=10.0)
    land_size: Optional[float] = Field(None, gt=0, le=10.0)
    crop_type: Optional[str] = None
    fpo_affiliation: Optional[str] = None

    def get_land_size(self) -> float:
        if self.land_size_acres is not None:
            return self.land_size_acres
        if self.land_size is not None:
            return self.land_size
        return 2.0


class FarmerUpdate(BaseModel):
    """Schema for updating a farmer"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    village: Optional[str] = Field(None, min_length=1, max_length=255)
    district: Optional[str] = Field(None, min_length=1, max_length=255)
    state: Optional[str] = Field(None, min_length=1, max_length=255)
    land_size_acres: Optional[float] = Field(None, gt=0, le=10.0)
    status: Optional[FarmerStatus] = None


class FarmerResponse(FarmerBase):
    """Schema for farmer response"""
    id: int
    status: FarmerStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreditAssessmentBase(BaseModel):
    """Base schema for Credit Assessment adhering to 0–100 score"""
    credit_score: int = Field(..., ge=0, le=100)
    loan_eligibility_amount: float = Field(..., ge=0)
    risk_category: str = Field(..., min_length=1, max_length=100)
    crop_name: Optional[str] = None
    acres: Optional[float] = None
    projected_yield: Optional[float] = None
    mandi_price_per_qtl: Optional[float] = None
    gross_revenue: Optional[float] = None
    total_expenses: Optional[float] = None
    net_profit: Optional[float] = None
    pmfby_insured: Optional[bool] = False
    bullet_repayment_date: Optional[datetime] = None
    status: Optional[str] = "PENDING_REVIEW"
    score_breakdown: Optional[str] = None
    lender_notes: Optional[str] = None
    notes: Optional[str] = None


class CreditAssessmentCreate(CreditAssessmentBase):
    """Schema for creating a credit assessment"""
    farmer_id: int


class CreditAssessmentResponse(CreditAssessmentBase):
    """Schema for credit assessment response"""
    id: int
    farmer_id: int
    assessment_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Underwriting Calculation Request Schema
class UnderwritingCalculateRequest(BaseModel):
    farmer_name: str
    phone: str
    crop_name: str
    acres: float = Field(..., gt=0, le=10.0)
    projected_yield: float = Field(..., gt=0)
    seeds_cost: float = Field(6000.0, ge=0)
    fertilizer_cost: float = Field(8000.0, ge=0)
    labour_cost: float = Field(8000.0, ge=0)
    irrigation_other_cost: float = Field(2000.0, ge=0)
    peer_guarantors_count: int = Field(3, ge=0, le=10)
    is_consistent_performer: bool = False
    custom_price: Optional[float] = None


# Peer Group Schemas
class PeerGroupCreate(BaseModel):
    group_code: str
    fpo_name: str
    village: str
    district: str
    member_farmer_ids: List[int] = Field(..., min_length=1, max_length=5)


class PeerGroupMemberResponse(BaseModel):
    id: int
    farmer_id: int
    farmer_name: Optional[str] = None
    phone: Optional[str] = None
    role: str
    guarantee_pledged: bool

    class Config:
        from_attributes = True


class PeerGroupResponse(BaseModel):
    id: int
    group_code: str
    fpo_name: str
    village: str
    district: str
    status: str
    repayment_rate: float
    created_at: datetime
    members: List[PeerGroupMemberResponse] = []

    class Config:
        from_attributes = True


# Crop Verification Schemas
class CropVerificationCreate(BaseModel):
    farmer_id: int
    crop_name: str
    verified_acres: float
    crop_stage: str
    sowing_date: Optional[datetime] = None
    expected_harvest_date: Optional[datetime] = None
    field_officer_name: str = "FPO Field Officer"
    verification_status: str = "VERIFIED"
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    notes: Optional[str] = None


class CropVerificationResponse(BaseModel):
    id: int
    farmer_id: int
    crop_name: str
    verified_acres: float
    crop_stage: str
    sowing_date: Optional[datetime]
    expected_harvest_date: Optional[datetime]
    field_officer_name: str
    verification_status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Lender Decision Schema
class LenderDecisionRequest(BaseModel):
    decision: str = Field(..., pattern="^(SANCTIONED|REJECTED|HOLD)$")
    sanctioned_amount: Optional[float] = None
    lender_notes: Optional[str] = None


# Voice & Consent Schemas
class VoiceParseRequest(BaseModel):
    transcript: str
    lang_code: str = "hi"


class ConsentRecordRequest(BaseModel):
    farmer_id: int
    consent_credit_assessment: bool = True
    consent_fpo_sharing: bool = True
    consent_mandi_alerts: bool = True
