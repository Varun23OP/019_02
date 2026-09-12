from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from backend.models import FarmerStatus


class FarmerBase(BaseModel):
    """Base schema for Farmer"""
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    village: str = Field(..., min_length=1, max_length=255)
    district: str = Field(..., min_length=1, max_length=255)
    state: str = Field(..., min_length=1, max_length=255)
    land_size_acres: float = Field(..., gt=0, le=2.5)

    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Phone number must contain only digits, +, -, and spaces')
        return v


class FarmerCreate(FarmerBase):
    """Schema for creating a farmer"""
    pass


class FarmerUpdate(BaseModel):
    """Schema for updating a farmer"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    village: Optional[str] = Field(None, min_length=1, max_length=255)
    district: Optional[str] = Field(None, min_length=1, max_length=255)
    state: Optional[str] = Field(None, min_length=1, max_length=255)
    land_size_acres: Optional[float] = Field(None, gt=0, le=2.5)
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
    """Base schema for Credit Assessment"""
    credit_score: int = Field(..., ge=0, le=1000)
    loan_eligibility_amount: float = Field(..., ge=0)
    risk_category: str = Field(..., min_length=1, max_length=50)
    notes: Optional[str] = Field(None, max_length=1000)


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
