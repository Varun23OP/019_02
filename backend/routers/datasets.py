"""
FastAPI Router for Live Agriculture Datasets & Telemetry (backend/routers/datasets.py)
"""

from fastapi import APIRouter
from backend.services.agronomic_engine import AgronomicEngine, DISTRICT_COORDINATES, NHB_YIELD_CEILINGS_QTL_ACRE

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])
engine = AgronomicEngine()

@router.get("/weather/{district}")
async def get_district_weather(district: str):
    """Fetches real-time micro-climate weather telemetry for a given district."""
    return engine.fetch_realtime_weather_telemetry(district)

@router.get("/nhb-benchmarks")
async def get_nhb_benchmarks():
    """Returns NHB 90th percentile yield ceilings and CACP expense norms."""
    return {"yield_ceilings_qtl_acre": NHB_YIELD_CEILINGS_QTL_ACRE}

@router.get("/districts")
async def get_supported_districts():
    """Returns all supported agricultural districts with APMC mandis."""
    return {"districts": DISTRICT_COORDINATES}
