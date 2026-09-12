from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from backend.services.agri_data import AgriDataService, AGMARKNET_MANDI_CATALOG, NHB_DISTRICT_YIELDS

router = APIRouter()


@router.get("/mandi-prices")
async def get_mandi_prices(crop_name: str = "Tomato (Horticulture)"):
    """
    Fetch daily mandi modal price and 30-day price trend from AGMARKNET.
    """
    return AgriDataService.get_mandi_price(crop_name)


@router.get("/all-crops")
async def list_available_crops():
    """List all supported crops with daily APMC benchmarks and MSP."""
    crops_summary = []
    for crop, data in AGMARKNET_MANDI_CATALOG.items():
        nhb = NHB_DISTRICT_YIELDS.get(crop, {})
        crops_summary.append({
            "crop_name": crop,
            "category": data["category"],
            "primary_mandi": data["primary_mandi"],
            "modal_price_per_qtl": data["modal_price_per_qtl"],
            "msp_benchmark": data["msp_benchmark"],
            "trend_30d_pct": data["trend_30d_pct"],
            "district_avg_yield": nhb.get("district_avg_yield", 15.0),
            "crop_duration_days": nhb.get("duration_days", 110)
        })
    return crops_summary


@router.get("/district-yield")
async def get_district_yield(crop_name: str = "Tomato (Horticulture)"):
    """Fetch NHB / DES district benchmark yield data."""
    return AgriDataService.get_district_yield(crop_name)


@router.get("/pmfby")
async def check_pmfby(phone: str, crop_name: Optional[str] = None):
    """Query PMFBY crop insurance registry."""
    return AgriDataService.check_pmfby_insurance(phone, crop_name)


@router.get("/alerts")
async def get_market_alerts(crop_name: str = "Tomato (Horticulture)", acres: float = 2.0):
    """Fetch proactive mandi price alerts and harvest timeline reminders."""
    bullet_date = datetime.utcnow() + timedelta(days=140)
    return AgriDataService.generate_alerts(crop_name, acres, bullet_date)
