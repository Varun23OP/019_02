"""
Pydantic Schemas for KisanSetu Agronomic Credit Underwriting
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CreditAssessmentRequest(BaseModel):
    farmer_name: str = Field(default="Ramesh Tukaram Patil", description="Full name of farmer")
    phone: str = Field(default="+91 98223 45678", description="DBT-linked phone")
    district: str = Field(default="Nashik", description="District name")
    state: str = Field(default="Maharashtra", description="State name")
    crop_name: str = Field(default="Tomato", description="Cultivated crop")
    land_acres: float = Field(default=1.5, ge=0.1, le=2.5, description="Marginal land area (< 2.5 acres)")
    expected_yield_qtl_acre: float = Field(default=20.0, description="Farmer reported yield")
    reported_cost_acre: Optional[float] = Field(default=38000.0, description="Cost of cultivation per acre")
    peer_member_ids: List[str] = Field(default=["MEM-442", "MEM-443"], description="FPO guarantor roster IDs")
    pm_kisan_verified: bool = Field(default=True)
    pmfby_enrolled: bool = Field(default=True)

class YieldCappingInfo(BaseModel):
    nhb_district_ceiling_qtl_acre: float
    reported_yield_qtl_acre: float
    effective_yield_qtl_acre: float
    yield_clamped: bool
    total_effective_yield_qtl: float
    cacp_cost_per_acre_inr: float
    total_cultivation_cost_inr: float
    growth_duration_days: int

class MandiPriceDiscovery(BaseModel):
    mandi_modal_price_qtl: float
    volatility_30d_pct: float
    haircut_applied: bool
    haircut_pct: float
    freight_deduction_inr_qtl: float
    net_farmgate_price_inr_qtl: float
    arrivals_tonnes: float
    price_trend_30d: str

class WeatherTelemetry(BaseModel):
    district: str
    temperature_c: float
    rainfall_7d_mm: float
    rainfall_status: str
    soil_moisture_index: float
    drought_risk_multiplier: float
    weather_maturity_delay_days: int
    source: str

class CreditAssessmentResponse(BaseModel):
    farmer_profile: Dict[str, Any]
    agronomic_guards: Dict[str, Any]
    financial_sizing: Dict[str, Any]
    trade_settlement_and_bullet_due: Dict[str, Any]

class BatchDisbursementRequest(BaseModel):
    farmer_ids: List[str]
    voucher_type: str = "e-RUPI Direct Input Voucher"
    authorized_by: str = "NABARD / RRB Consortium Desk"
