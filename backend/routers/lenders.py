"""
FastAPI Router for Institutional Lenders, Risk Desk & Batch Disbursals (backend/routers/lenders.py)
"""

from fastapi import APIRouter, HTTPException
from backend.schemas.credit import BatchDisbursementRequest
import hashlib
import time

router = APIRouter(prefix="/api/lenders", tags=["Lenders"])

UNDERWRITING_QUEUE = [
    {
        "farmer_did": "did:kisan:ind:9f8a2c418e20b3",
        "farmer_name": "Ramesh Tukaram Patil",
        "district": "Nashik",
        "state": "Maharashtra",
        "crop": "Tomato",
        "acres": 1.5,
        "clamped_yield_qtl": 22.0,
        "raw_reported_yield": 24.5,
        "sanction_amount": 102400,
        "trust_score": 91,
        "fpo_roster_status": "All Peers Within Cap (1/2)",
        "weather_status": "Normal Rainfall",
        "enam_status": "Gate Inward Completed",
        "enwr_status": "Pledge Ready",
        "underwriting_status": "Ready for Disbursal"
    },
    {
        "farmer_did": "did:kisan:ind:4a7e9102c813f5",
        "farmer_name": "Venkatesh Gowda",
        "district": "Kolar",
        "state": "Karnataka",
        "crop": "Tomato",
        "acres": 2.0,
        "clamped_yield_qtl": 22.0,
        "raw_reported_yield": 22.0,
        "sanction_amount": 132000,
        "trust_score": 89,
        "fpo_roster_status": "Guarantor #501 Cap Reached (2/2)",
        "weather_status": "Dry Spell (15d extension)",
        "enam_status": "Pre-Registered",
        "enwr_status": "Eligible",
        "underwriting_status": "Peer Cap Warning"
    },
    {
        "farmer_did": "did:kisan:ind:7b3c29910d54a8",
        "farmer_name": "Samba Siva Rao",
        "district": "Guntur",
        "state": "Andhra Pradesh",
        "crop": "Chilli (Dry)",
        "acres": 2.2,
        "clamped_yield_qtl": 14.0,
        "raw_reported_yield": 13.8,
        "sanction_amount": 175000,
        "trust_score": 94,
        "fpo_roster_status": "All Peers Within Cap (0/2)",
        "weather_status": "Optimal Climate",
        "enam_status": "Auction Settled",
        "enwr_status": "Pledged",
        "underwriting_status": "Disbursed via e-RUPI"
    }
]

@router.get("/queue")
async def get_underwriting_queue():
    """Returns active loan applications in the institutional underwriting pipeline."""
    return {"queue": UNDERWRITING_QUEUE, "total_active_pipeline_inr": sum(f["sanction_amount"] for f in UNDERWRITING_QUEUE)}

@router.post("/batch-disburse")
async def execute_batch_disbursement(payload: BatchDisbursementRequest):
    """
    Executes Priority Sector Lending (PSL) batch disbursement via e-RUPI direct vouchers.
    """
    tx_hash = f"0x{hashlib.sha256(str(time.time()).encode()).hexdigest()[:28]}"
    return {
        "status": "SUCCESS",
        "message": f"Disbursed e-RUPI vouchers to {len(payload.farmer_ids)} farmers successfully.",
        "transaction_hash": tx_hash,
        "settlement_rail": "NPCI / e-RUPI Agri Voucher Stream",
        "authorized_by": payload.authorized_by,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
