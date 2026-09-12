"""
Comprehensive Verification and Test Suite for KisanSetu
Verifies all PRD criteria across:
- Farmer Experience & Voice Intake
- Credit Assessment & Agricultural Data (AGMARKNET, NHB, PMFBY)
- 5-Second Latency Benchmark (< 5000ms)
- FPO Coordinator 3-Peer Groups & Crop Verification
- Rural Lender Decisioning & Harvest Bullet Repayments
- Farmer DID Cryptographic Verifiable Credentials & GDPR Compliance
"""

import time
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_and_root():
    """Verify health and root discovery endpoints."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "operational"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"
    print("PASS: test_health_and_root")


def test_underwriting_latency_benchmark():
    """Verify PRD Requirement: Credit calculations complete in under 5 seconds."""
    payload = {
        "farmer_name": "Ramesh Patel",
        "phone": "9876543210",
        "crop_name": "Tomato (Horticulture)",
        "acres": 2.0,
        "projected_yield": 18.0,
        "seeds_cost": 6000.0,
        "fertilizer_cost": 8000.0,
        "labour_cost": 8000.0,
        "irrigation_other_cost": 2000.0,
        "peer_guarantors_count": 3,
        "is_consistent_performer": False
    }
    t0 = time.perf_counter()
    res = client.post("/api/v1/underwriting/calculate", json=payload)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert res.status_code == 200
    data = res.json()
    assert elapsed_ms < 5000.0, f"Calculation exceeded 5000ms: {elapsed_ms}ms"
    assert data["sla_performance"]["is_under_5_seconds"] is True

    # Check PRD formulas
    # Gross Revenue = Acres (2.0) * Yield (18.0) * Mandi Price (2250.0) = 81000
    assert data["gross_revenue"] == 81000.0
    # Total Expenses = 6000 + 8000 + 8000 + 2000 = 24000
    assert data["expenses_breakdown"]["total"] == 24000.0
    # Net Profit = 81000 - 24000 = 57000
    assert data["net_profit"] == 57000.0
    # Credit Limit = 0.45 * 57000 = 25650.0
    assert data["credit_limit"] == 25650.0
    # 0–100 Credit Score
    assert 0 <= data["credit_score"] <= 100
    assert data["credit_score"] >= 80  # Low risk tier
    # Harvest-synchronized bullet repayment
    assert data["amortization"]["monthly_emi_inr"] == 0.0
    assert "bullet_due_date" in data["amortization"]
    # Explainability factors present
    assert len(data["score_factors"]) >= 4
    print(f"PASS: test_underwriting_latency_benchmark (Elapsed: {elapsed_ms:.2f}ms < 5000ms)")


def test_consistent_performer_booster():
    """Verify PRD Requirement: Higher limits for consistent performers."""
    base_payload = {
        "farmer_name": "Ramesh Patel",
        "phone": "9876543210",
        "crop_name": "Tomato (Horticulture)",
        "acres": 2.0,
        "projected_yield": 18.0,
        "seeds_cost": 6000.0,
        "fertilizer_cost": 8000.0,
        "labour_cost": 8000.0,
        "irrigation_other_cost": 2000.0,
        "peer_guarantors_count": 3,
        "is_consistent_performer": False
    }
    res_base = client.post("/api/v1/underwriting/calculate", json=base_payload).json()

    boosted_payload = dict(base_payload)
    boosted_payload["is_consistent_performer"] = True
    res_boosted = client.post("/api/v1/underwriting/calculate", json=boosted_payload).json()

    # Verify +15% credit limit boost
    expected_boosted = round(res_base["base_credit_limit"] * 1.15, 2)
    assert res_boosted["credit_limit"] == expected_boosted
    assert res_boosted["credit_score"] >= res_base["credit_score"]
    print("PASS: test_consistent_performer_booster")


def test_agricultural_market_data_endpoints():
    """Verify AGMARKNET, NHB, and PMFBY integrations."""
    # AGMARKNET Mandi Price
    res_mandi = client.get("/api/v1/market-data/mandi-prices?crop_name=Tomato")
    assert res_mandi.status_code == 200
    mandi_data = res_mandi.json()
    assert mandi_data["modal_price_per_qtl"] == 2250.0
    assert "Nashik APMC" in mandi_data["primary_mandi"]
    assert len(mandi_data["historical_30d_prices"]) == 30

    # NHB District Yield Benchmark
    res_yield = client.get("/api/v1/market-data/district-yield?crop_name=Tomato")
    assert res_yield.status_code == 200
    assert res_yield.json()["district_avg_yield"] == 17.5

    # PMFBY Insurance Verification
    res_pmfby = client.get("/api/v1/market-data/pmfby?phone=9876543210")
    assert res_pmfby.status_code == 200
    assert res_pmfby.json()["is_insured"] is True
    assert "PMFBY" in res_pmfby.json()["policy_number"]

    # Proactive Market Alerts
    res_alerts = client.get("/api/v1/market-data/alerts?crop_name=Tomato&acres=2.0")
    assert res_alerts.status_code == 200
    assert len(res_alerts.json()) >= 2
    print("PASS: test_agricultural_market_data_endpoints")


def test_voice_intake_10_plus_languages():
    """Verify PRD Requirement: Voice recognition targeting 10+ languages."""
    res_langs = client.get("/api/v1/voice/languages")
    assert res_langs.status_code == 200
    langs = res_langs.json()
    assert langs["supported_languages_count"] >= 10, f"Expected >= 10 languages, found {langs['supported_languages_count']}"

    # Test sample vernacular voice retrieval and parsing for Hindi, Marathi, Gujarati, Telugu, Tamil
    for code in ["hi", "mr", "gu", "te", "ta", "kn", "pa", "bn", "or", "as", "en"]:
        sample_res = client.get(f"/api/v1/voice/sample/{code}")
        assert sample_res.status_code == 200
        transcript = sample_res.json()["sample_data"]["transcript"]
        assert len(transcript) > 10

        # Parse transcript to structured form fields
        parse_res = client.post("/api/v1/voice/parse", json={"transcript": transcript, "lang_code": code})
        assert parse_res.status_code == 200
        mapped = parse_res.json()["mapped_fields"]
        assert mapped["acres"] > 0
        assert mapped["projected_yield"] > 0
        assert mapped["input_costs"] > 0
        assert parse_res.json()["requires_review"] is True
    print("PASS: test_voice_intake_10_plus_languages (Tested all 11 languages)")


def test_fpo_coordinator_workflows():
    """Verify FPO 3-member peer group onboarding, field crop verification, and distress detection."""
    # 1. Onboard 3-Member Peer Group
    group_payload = {
        "group_code": f"GRP-TEST-{int(time.time())}",
        "fpo_name": "Sahyadri Agro Producer Co.",
        "village": "Pimpalgaon",
        "district": "Nashik",
        "member_farmer_ids": [1, 2, 3]
    }
    res_group = client.post("/api/v1/fpo/groups", json=group_payload)
    assert res_group.status_code == 201
    assert res_group.json()["member_count"] == 3

    # 2. Record Field Crop Verification
    ver_payload = {
        "farmer_id": 1,
        "crop_name": "Tomato (Horticulture)",
        "verified_acres": 2.0,
        "crop_stage": "Flowering & Fruit Setting",
        "field_officer_name": "Field Officer Anand",
        "verification_status": "VERIFIED",
        "notes": "Verified in person. Staked tomatoes on trellis with drip lines."
    }
    res_ver = client.post("/api/v1/fpo/verifications", json=ver_payload)
    assert res_ver.status_code == 201
    assert res_ver.json()["verification_status"] == "VERIFIED"

    # 3. Retrieve Peer Groups
    res_list = client.get("/api/v1/fpo/groups")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 4. Check Peer Support Alerts
    res_alerts = client.get("/api/v1/fpo/alerts")
    assert res_alerts.status_code == 200
    assert len(res_alerts.json()) >= 1
    print("PASS: test_fpo_coordinator_workflows")


def test_lender_underwriting_and_disbursement():
    """Verify Rural Bank Lender console, decisioning, and e-RUPI disbursement."""
    # 1. List applications
    res_apps = client.get("/api/v1/lenders/applications")
    assert res_apps.status_code == 200
    apps = res_apps.json()
    assert len(apps) >= 1
    target_assessment_id = apps[0]["assessment_id"]

    # 2. Lender Sanction Decision
    decision_payload = {
        "decision": "SANCTIONED",
        "sanctioned_amount": 25650.0,
        "lender_notes": "Sanctioned under Priority Sector Lending. Crop verified by FPO coordinator."
    }
    res_decision = client.post(f"/api/v1/lenders/applications/{target_assessment_id}/decision", json=decision_payload)
    assert res_decision.status_code == 200
    assert res_decision.json()["status"] == "SANCTIONED"

    # 3. Instant e-RUPI Disbursement
    res_disburse = client.post(f"/api/v1/lenders/applications/{target_assessment_id}/disburse")
    assert res_disburse.status_code == 200
    assert res_disburse.json()["status"] == "DISBURSED"
    assert "e-RUPI" in res_disburse.json()["disbursement_channel"]
    print("PASS: test_lender_underwriting_and_disbursement")


def test_farmer_identity_and_gdpr():
    """Verify W3C DID, Verifiable Credential authenticity, and GDPR compliance."""
    # 1. Export Verifiable Credential
    res_vc = client.get("/api/v1/identity/farmer/1/credential")
    assert res_vc.status_code == 200
    vc = res_vc.json()
    assert vc["type"] == ["VerifiableCredential", "AgronomicCreditCredential"]
    assert "did:kisan:" in vc["credentialSubject"]["id"]
    assert "proof" in vc

    # 2. Verify Credential Document
    res_verify = client.post("/api/v1/identity/verify-credential", json=vc)
    assert res_verify.status_code == 200
    assert res_verify.json()["is_valid"] is True
    assert res_verify.json()["verification_status"] == "SIGNATURE_VERIFIED_AUTHENTIC"

    # 3. Capture GDPR Consent
    consent_payload = {
        "farmer_id": 1,
        "consent_credit_assessment": True,
        "consent_fpo_sharing": True,
        "consent_mandi_alerts": True
    }
    res_consent = client.post("/api/v1/identity/consent", json=consent_payload)
    assert res_consent.status_code == 200
    assert res_consent.json()["data_minimization_verified"] is True

    # 4. GDPR Article 15/20 Data Dossier Export
    res_export = client.get("/api/v1/identity/gdpr/export/1")
    assert res_export.status_code == 200
    assert res_export.json()["dossier_type"] == "GDPR_PORTABLE_DATA_EXPORT"
    print("PASS: test_farmer_identity_and_gdpr")


if __name__ == "__main__":
    print("--- RUNNING KISANSETU AUTOMATED TEST SUITE ---")
    test_health_and_root()
    test_underwriting_latency_benchmark()
    test_consistent_performer_booster()
    test_agricultural_market_data_endpoints()
    test_voice_intake_10_plus_languages()
    test_fpo_coordinator_workflows()
    test_lender_underwriting_and_disbursement()
    test_farmer_identity_and_gdpr()
    print("--- ALL TESTS PASSED SUCCESSFULLY! ---")
