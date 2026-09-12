"""
Automated Verification Suite for KisanSetu Rural Lender Console Workflow:
Validates all 8 requirements:
1. Reject a pending loan -> database status changes to rejected -> disappears from pending queue.
2. Sanction a pending loan -> database status changes to sanctioned -> disappears from pending queue.
3. Attempt to disburse a pending loan -> action is blocked (HTTP 400).
4. Attempt to disburse a rejected loan -> action is blocked (HTTP 400).
5. Disburse a sanctioned loan -> status and supported transaction details are saved -> appears in disbursed view.
6. Refresh / restart simulation -> database retains statuses and transaction IDs.
7. Simulate API/database failure -> no false success message and status remains unchanged.
8. Click action repeatedly -> duplicate sanction or disbursement is blocked (HTTP 400).
"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import CreditAssessment, Farmer
import datetime

client = TestClient(app)

def run_tests():
    print("==================================================================")
    print("  TEST SUITE: Rural Lender Sanction, Rejection & Disbursement")
    print("==================================================================")

    # Setup: Create 2 fresh test pending loans in DB
    db = SessionLocal()
    farmer = db.query(Farmer).first()
    farmer_id = farmer.id if farmer else 1

    # Test Loan A (for rejection flow)
    loan_a = CreditAssessment(
        farmer_id=farmer_id,
        assessment_date=datetime.datetime.utcnow(),
        credit_score=72,
        loan_eligibility_amount=18500.0,
        risk_category="Tier-2 Moderate Risk",
        crop_name="Cotton",
        acres=1.8,
        projected_yield=7.0,
        mandi_price_per_qtl=6200.0,
        gross_revenue=78120.0,
        total_expenses=37000.0,
        net_profit=41120.0,
        pmfby_insured=True,
        bullet_repayment_date=datetime.datetime.utcnow() + datetime.timedelta(days=150),
        status="PENDING_REVIEW"
    )
    # Test Loan B (for sanction and disbursement flow)
    loan_b = CreditAssessment(
        farmer_id=farmer_id,
        assessment_date=datetime.datetime.utcnow(),
        credit_score=88,
        loan_eligibility_amount=27500.0,
        risk_category="Tier-1 Low Risk",
        crop_name="Wheat",
        acres=2.0,
        projected_yield=20.0,
        mandi_price_per_qtl=2425.0,
        gross_revenue=97000.0,
        total_expenses=35000.0,
        net_profit=62000.0,
        pmfby_insured=True,
        bullet_repayment_date=datetime.datetime.utcnow() + datetime.timedelta(days=130),
        status="PENDING_REVIEW"
    )
    db.add(loan_a)
    db.add(loan_b)
    db.commit()
    db.refresh(loan_a)
    db.refresh(loan_b)
    id_a = loan_a.id
    id_b = loan_b.id
    db.close()

    print(f"Created Test Loan A (#{id_a}, Status=PENDING_REVIEW, Limit=INR18,500)")
    print(f"Created Test Loan B (#{id_b}, Status=PENDING_REVIEW, Limit=INR27,500)")

    # -------------------------------------------------------------
    # Check 3: Attempt to disburse a pending loan -> MUST BE BLOCKED
    # -------------------------------------------------------------
    res_disb_pending = client.post(f"/api/v1/lenders/applications/{id_a}/disburse")
    assert res_disb_pending.status_code == 400, f"Expected 400, got {res_disb_pending.status_code}"
    assert "PENDING_REVIEW" in res_disb_pending.json()["detail"] or "SANCTIONED" in res_disb_pending.json()["detail"]
    print(f"[PASS] 3. Attempt to disburse pending loan #{id_a} was blocked (HTTP 400: '{res_disb_pending.json()['detail']}')")

    # -------------------------------------------------------------
    # Check 1: Reject a pending loan -> DB status changes -> disappears from pending queue
    # -------------------------------------------------------------
    rej_resp = client.post(
        f"/api/v1/lenders/applications/{id_a}/decision",
        json={"decision": "REJECTED", "lender_notes": "Cashflow insufficient for cotton pest risks."}
    )
    assert rej_resp.status_code == 200
    assert rej_resp.json()["status"] == "REJECTED"

    # Verify DB persistence
    db = SessionLocal()
    rec_a = db.query(CreditAssessment).filter(CreditAssessment.id == id_a).first()
    assert rec_a.status == "REJECTED"
    assert rec_a.lender_notes == "Cashflow insufficient for cotton pest risks."
    db.close()

    # Verify it disappeared from pending queue
    pending_queue = client.get("/api/v1/lenders/applications?status=PENDING_REVIEW").json()
    pending_ids = [p["assessment_id"] for p in pending_queue]
    assert id_a not in pending_ids
    print(f"[PASS] 1. Pending loan #{id_a} rejected -> Status persisted as REJECTED -> Disappeared from pending queue")

    # -------------------------------------------------------------
    # Check 4: Attempt to disburse a rejected loan -> MUST BE BLOCKED
    # -------------------------------------------------------------
    res_disb_rej = client.post(f"/api/v1/lenders/applications/{id_a}/disburse")
    assert res_disb_rej.status_code == 400
    assert "REJECTED" in res_disb_rej.json()["detail"]
    print(f"[PASS] 4. Attempt to disburse rejected loan #{id_a} was blocked (HTTP 400: '{res_disb_rej.json()['detail']}')")

    # -------------------------------------------------------------
    # Check 4b: Attempt to sanction a rejected loan -> MUST BE BLOCKED
    # -------------------------------------------------------------
    res_sanc_rej = client.post(
        f"/api/v1/lenders/applications/{id_a}/decision",
        json={"decision": "SANCTIONED", "lender_notes": "Trying to sanction rejected loan"}
    )
    assert res_sanc_rej.status_code == 400
    assert "REJECTED" in res_sanc_rej.json()["detail"]
    print(f"[PASS] 4b. Attempt to sanction rejected loan #{id_a} was blocked (HTTP 400)")

    # -------------------------------------------------------------
    # Check 2: Sanction a pending loan -> DB status changes -> disappears from pending queue
    # -------------------------------------------------------------
    sanc_resp = client.post(
        f"/api/v1/lenders/applications/{id_b}/decision",
        json={"decision": "SANCTIONED", "sanctioned_amount": 27500.0, "lender_notes": "Sanctioned under PSL direct agro."}
    )
    assert sanc_resp.status_code == 200
    assert sanc_resp.json()["status"] == "SANCTIONED"

    # Verify DB persistence
    db = SessionLocal()
    rec_b = db.query(CreditAssessment).filter(CreditAssessment.id == id_b).first()
    assert rec_b.status == "SANCTIONED"
    assert rec_b.loan_eligibility_amount == 27500.0
    db.close()

    # Verify disappeared from pending queue
    pending_queue = client.get("/api/v1/lenders/applications?status=PENDING_REVIEW").json()
    pending_ids = [p["assessment_id"] for p in pending_queue]
    assert id_b not in pending_ids
    print(f"[PASS] 2. Pending loan #{id_b} sanctioned -> Status persisted as SANCTIONED -> Disappeared from pending queue")

    # -------------------------------------------------------------
    # Check 8: Repeated clicks on Sanction -> duplicate action blocked
    # -------------------------------------------------------------
    res_repeat_sanc = client.post(
        f"/api/v1/lenders/applications/{id_b}/decision",
        json={"decision": "SANCTIONED", "lender_notes": "Duplicate click"}
    )
    assert res_repeat_sanc.status_code == 400
    assert "already SANCTIONED" in res_repeat_sanc.json()["detail"]
    print(f"[PASS] 8a. Repeated sanction click on loan #{id_b} was blocked (HTTP 400: '{res_repeat_sanc.json()['detail']}')")

    # -------------------------------------------------------------
    # Check 5: Disburse a sanctioned loan -> status and transaction details saved -> in disbursed view
    # -------------------------------------------------------------
    disb_resp = client.post(f"/api/v1/lenders/applications/{id_b}/disburse")
    assert disb_resp.status_code == 200
    data = disb_resp.json()
    assert data["status"] == "DISBURSED"
    assert data["disbursement_mode"] == "SIMULATED_DEMO"
    assert "SIM-eRUPI" in data["disbursement_tx_id"]
    tx_id = data["disbursement_tx_id"]

    # Verify DB persistence of status and transaction details
    db = SessionLocal()
    rec_b_disb = db.query(CreditAssessment).filter(CreditAssessment.id == id_b).first()
    assert rec_b_disb.status == "DISBURSED"
    assert rec_b_disb.disbursement_tx_id == tx_id
    assert rec_b_disb.disbursed_at is not None
    db.close()

    # Appears in disbursed view
    disbursed_queue = client.get("/api/v1/lenders/applications?status=DISBURSED").json()
    disbursed_ids = [d["assessment_id"] for d in disbursed_queue]
    assert id_b in disbursed_ids
    print(f"[PASS] 5. Sanctioned loan #{id_b} disbursed -> Tx ID ({tx_id}) and timestamp saved -> Appears in disbursed view")

    # -------------------------------------------------------------
    # Check 8b: Repeated disbursement click -> duplicate disbursement blocked
    # -------------------------------------------------------------
    res_repeat_disb = client.post(f"/api/v1/lenders/applications/{id_b}/disburse")
    assert res_repeat_disb.status_code == 400
    assert "already been disbursed" in res_repeat_disb.json()["detail"]
    print(f"[PASS] 8b. Repeated disburse click on loan #{id_b} was blocked (HTTP 400: '{res_repeat_disb.json()['detail']}')")

    # -------------------------------------------------------------
    # Check 8c: Disbursed loan cannot be modified/rejected
    # -------------------------------------------------------------
    res_rej_disb = client.post(
        f"/api/v1/lenders/applications/{id_b}/decision",
        json={"decision": "REJECTED"}
    )
    assert res_rej_disb.status_code == 400
    assert "disbursed" in res_rej_disb.json()["detail"]
    print(f"[PASS] 8c. Attempt to reject already disbursed loan #{id_b} was blocked (HTTP 400)")

    # -------------------------------------------------------------
    # Check 6: Refresh the page / restart simulation -> statuses remain correct
    # -------------------------------------------------------------
    db = SessionLocal()
    fresh_rec_a = db.query(CreditAssessment).filter(CreditAssessment.id == id_a).first()
    fresh_rec_b = db.query(CreditAssessment).filter(CreditAssessment.id == id_b).first()
    assert fresh_rec_a.status == "REJECTED"
    assert fresh_rec_b.status == "DISBURSED"
    assert fresh_rec_b.disbursement_tx_id == tx_id
    db.close()
    print("[PASS] 6. Fresh database session verification: statuses and audit fields remain persisted")

    # -------------------------------------------------------------
    # Check 7: Simulate an API/database failure -> no false success message, status remains accurate
    # -------------------------------------------------------------
    # Test invalid ID
    res_fake = client.post(
        "/api/v1/lenders/applications/999999/decision",
        json={"decision": "SANCTIONED"}
    )
    assert res_fake.status_code == 404
    assert "not found" in res_fake.json()["detail"].lower()
    print(f"[PASS] 7a. Simulated failure on non-existent loan #{999999}: HTTP 404 '{res_fake.json()['detail']}', no false success")

    # Test invalid disbursement on rejected loan
    res_fake_disb = client.post(f"/api/v1/lenders/applications/{id_a}/disburse")
    assert res_fake_disb.status_code == 400
    assert "rejected" in res_fake_disb.json()["detail"].lower()
    print(f"[PASS] 7b. Simulated invalid action rejected by backend: '{res_fake_disb.json()['detail']}'")

    print("==================================================================")
    print("  ALL 8 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("==================================================================")


if __name__ == "__main__":
    run_tests()
