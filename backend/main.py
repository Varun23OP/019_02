"""
KisanSetu Backend Application (FastAPI)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.routers import (
    farmers,
    underwriting,
    fpo,
    lenders,
    market_data,
    voice_intake,
    identity,
    datasets,
    voice
)
from backend.config import settings
from backend.database import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting KisanSetu Farmer Financial Infrastructure API")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified / created")
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title="KisanSetu Financial Infrastructure & Agronomic Underwriting API",
    description="Community-Owned Credit Network for Marginal Farmers: Deterministic Agronomic Underwriting, FPO 3-Peer Social Collateral, Harvest Bullet Repayment",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register All API Routers
app.include_router(farmers.router, prefix="/api/v1/farmers", tags=["Farmers"])
app.include_router(underwriting.router, prefix="/api/v1/underwriting", tags=["Agronomic Underwriting"])
app.include_router(fpo.router, prefix="/api/v1/fpo", tags=["FPO Coordinator & Peer Groups"])
app.include_router(lenders.router, prefix="/api/v1/lenders", tags=["Rural Lender Console"])
app.include_router(market_data.router, prefix="/api/v1/market-data", tags=["Agricultural Market Data"])
app.include_router(voice_intake.router, prefix="/api/v1/voice", tags=["Multilingual Voice Intake"])
app.include_router(identity.router, prefix="/api/v1/identity", tags=["Identity, DID & GDPR"])

# Legacy / Conversational Routers from origin
app.include_router(datasets.router)
app.include_router(voice.router)


@app.get("/")
async def root():
    """Root endpoint with API capabilities overview"""
    return {
        "service": "KisanSetu Dynamic Agronomic Credit Engine",
        "status": "ONLINE",
        "version": "2.0.0",
        "docs_url": "/docs",
        "features": {
            "deterministic_underwriting": "Acres × Yield × Price, 0.45 × Net Profit, 0-100 Explainable Score",
            "agri_data_integration": "AGMARKNET Mandi Modal Prices, NHB District Yields, PMFBY Records",
            "fpo_social_collateral": "3-Member Peer Guarantee Groups & Field Crop Verification",
            "lender_console": "Harvest Bullet Repayments & e-RUPI Voucher Disbursement",
            "voice_intake": "10+ Regional Languages with Transcript-to-Field Mapping",
            "portable_identity": "W3C Verifiable Credentials & GDPR Compliance"
        },
        "datasets_integrated": [
            "AGMARKNET 2.0 Live Mandi Prices",
            "NHB 90th-Percentile Yield Ceilings",
            "CACP Crop Cultivation Schedules",
            "Open-Meteo Micro-Climate Telemetry",
            "PM-KISAN OGD Registry",
            "FPO Joint-Liability Exposure Caps",
            "e-NAM & WDRA e-NWR Settlement Tracking"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": logging.time.strftime("%Y-%m-%dT%H:%M:%SZ", logging.time.gmtime())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
