"""
KisanSetu Backend Application (FastAPI)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.routers import farmers, lenders, datasets, voice

app = FastAPI(
    title="KisanSetu Agronomic Credit & Underwriting API",
    version="2.0.0",
    description="Real-time agronomic underwriting network integrating AGMARKNET, NHB yield ceilings, Open-Meteo weather telemetry, and FPO joint-liability caps."
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(farmers.router)
app.include_router(lenders.router)
app.include_router(datasets.router)
app.include_router(voice.router)

@app.get("/")
async def root():
    return {
        "service": "KisanSetu Dynamic Agronomic Credit Engine",
        "status": "ONLINE",
        "version": "2.0.0",
        "docs_url": "/docs",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
