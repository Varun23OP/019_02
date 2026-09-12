"""
Verification Suite: Farmer Intake to FPO Guarantee Pool Integration
Validates:
1. Intake submission persists Farmer and CreditAssessment to DB.
2. Unassigned farmers appear in FPO dashboard under /unassigned-farmers.
3. Strict 3-member rule: Full pools (3/3) reject 4th member.
4. Open pools (< 3) accept assignment and recalculate pool credit capacity dynamically.
5. Assigned farmers appear with name, role, score, limit, guarantee status in their pool.
6. Intake with target open pool links immediately; intake with full pool falls back to unassigned queue.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def run_integration_tests():
    print("==================================================================")
    print("  TEST SUITE: Farmer Intake <-> FPO Guarantee Pool Integration")
    print("==================================================================")

    # 1. Submit Farmer Intake without pool (Default / Unassigned workflow)
    soha_phone = f"886676{int(time.time()) % 10000:04d}"
    intake_payload = {
        "farmer_name": "Soha Sharma",
        "phone": soha_phone,
        "village": "Pimpalgaon Baswant",
        "district": "Nashik",
        "state": "Maharashtra",
        "fpo_name": "Sahyadri Agro Producer Co.",
        "target_pool_id": None,
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

    res_intake = client.post("/api/v1/underwriting/submit-application", json=intake_payload)
    assert res_intake.status_code in [200, 201], f"Intake submission failed: {res_intake.text}"
    intake_data = res_intake.json()
    soha_id = intake_data["farmer_id"]
    soha_limit = intake_data["underwriting_result"]["credit_limit"]
    soha_score = intake_data["underwriting_result"]["credit_score"]
    assert intake_data["pool_assignment"]["status"] == "UNASSIGNED"
    print(f"[PASS] 1. Farmer Soha onboarded (ID: {soha_id}, Limit: INR{soha_limit:,.0f}, Score: {soha_score})")

    # 2. Verify Soha appears in Unassigned Farmers Queue
    res_unassigned = client.get("/api/v1/fpo/unassigned-farmers")
    assert res_unassigned.status_code == 200
    unassigned_list = res_unassigned.json()
    soha_entry = next((f for f in unassigned_list if f["farmer_id"] == soha_id), None)
    assert soha_entry is not None, f"Soha (ID {soha_id}) not found in unassigned queue!"
    assert soha_entry["name"] == "Soha Sharma"
    assert soha_entry["village"] == "Pimpalgaon Baswant"
    assert soha_entry["fpo_name"] == "Sahyadri Agro Producer Co."
    assert soha_entry["crop_name"] == "Tomato (Horticulture)"
    assert soha_entry["credit_limit"] == soha_limit
    assert soha_entry["credit_score"] == soha_score
    print(f"[PASS] 2. Soha verified in FPO Unassigned Farmers Queue")

    # 3. Fetch current groups and verify strict 3-member enforcement on full pools
    res_groups = client.get("/api/v1/fpo/groups")
    assert res_groups.status_code == 200
    groups = res_groups.json()
    full_group = next((g for g in groups if g.get("is_full") or g.get("member_count") >= 3), None)
    assert full_group is not None, "Expected at least one full 3-member seed group"
    
    # Attempting to assign Soha to an already full group must be rejected!
    res_overflow = client.post("/api/v1/fpo/assign-member", json={
        "farmer_id": soha_id,
        "group_id": full_group["id"],
        "role": "MEMBER",
        "guarantee_pledged": True
    })
    assert res_overflow.status_code == 400, f"Expected 400 rejection for full pool, got {res_overflow.status_code}"
    print(f"[PASS] 3. Strict 3-Member Rule preserved: Cannot add 4th member to pool {full_group['group_code']}")

    # 4. Form New 3-Member Guarantee Pool with Soha
    new_pool_code = f"GRP-SOHA-{int(time.time()) % 10000}"
    res_new_group = client.post("/api/v1/fpo/groups", json={
        "group_code": new_pool_code,
        "fpo_name": "Sahyadri Agro Producer Co.",
        "village": "Pimpalgaon Baswant",
        "district": "Nashik",
        "member_farmer_ids": [soha_id]
    })
    assert res_new_group.status_code == 201
    new_group_id = res_new_group.json()["group_id"]
    print(f"[PASS] 4. New forming pool {new_pool_code} created with Soha as Leader (1/3 members)")

    # 5. Verify Soha is no longer in unassigned queue
    res_unassigned2 = client.get("/api/v1/fpo/unassigned-farmers")
    assert res_unassigned2.status_code == 200
    soha_unassigned2 = next((f for f in res_unassigned2.json() if f["farmer_id"] == soha_id), None)
    assert soha_unassigned2 is None, "Soha still shows as unassigned after being assigned to pool!"
    print(f"[PASS] 5. Soha removed from unassigned queue")

    # 6. Verify Soha appears in live FPO Groups listing inside her pool
    res_groups2 = client.get("/api/v1/fpo/groups")
    assert res_groups2.status_code == 200
    soha_group = next((g for g in res_groups2.json() if g["id"] == new_group_id), None)
    assert soha_group is not None
    assert soha_group["member_count"] == 1
    assert soha_group["pool_state"] == "Forming (1/3)"
    assert soha_group["total_pool_credit_limit"] == soha_limit
    member_names = [m["name"] for m in soha_group["members"]]
    assert "Soha Sharma" in member_names
    soha_member_obj = next(m for m in soha_group["members"] if m["name"] == "Soha Sharma")
    assert soha_member_obj["role"] == "LEADER"
    assert soha_member_obj["credit_score"] == soha_score
    assert soha_member_obj["credit_limit"] == soha_limit
    assert soha_member_obj["guarantee_pledged"] is True
    print(f"[PASS] 6. Soha appears in live pool with correct details and dynamic limit INR{soha_group['total_pool_credit_limit']:,.0f}")

    # 7. Add Farmer 2 (Rohan) to open pool via /fpo/assign-member
    rohan_phone = f"886677{int(time.time()) % 10000:04d}"
    intake_rohan = client.post("/api/v1/underwriting/submit-application", json={
        "farmer_name": "Rohan Deshmukh",
        "phone": rohan_phone,
        "village": "Pimpalgaon",
        "district": "Nashik",
        "crop_name": "Tomato (Horticulture)",
        "acres": 1.5,
        "projected_yield": 18.0,
        "seeds_cost": 5000.0,
        "fertilizer_cost": 6000.0,
        "labour_cost": 6000.0,
        "irrigation_other_cost": 1500.0,
        "peer_guarantors_count": 3
    })
    rohan_data = intake_rohan.json()
    rohan_id = rohan_data["farmer_id"]
    rohan_limit = rohan_data["underwriting_result"]["credit_limit"]

    res_assign_rohan = client.post("/api/v1/fpo/assign-member", json={
        "farmer_id": rohan_id,
        "group_id": new_group_id,
        "role": "MEMBER",
        "guarantee_pledged": True
    })
    assert res_assign_rohan.status_code == 200
    assert res_assign_rohan.json()["member_count"] == 2
    assert res_assign_rohan.json()["total_pool_credit_limit"] == soha_limit + rohan_limit
    print(f"[PASS] 7. Rohan Deshmukh added to pool (2/3 members). Dynamic pool limit: INR{soha_limit + rohan_limit:,.0f}")

    # 8. Add Farmer 3 (Pooja) to reach full 3/3 capacity
    pooja_phone = f"886678{int(time.time()) % 10000:04d}"
    intake_pooja = client.post("/api/v1/underwriting/submit-application", json={
        "farmer_name": "Pooja Jadhav",
        "phone": pooja_phone,
        "village": "Pimpalgaon",
        "district": "Nashik",
        "crop_name": "Tomato (Horticulture)",
        "acres": 1.8,
        "projected_yield": 18.0,
        "seeds_cost": 5500.0,
        "fertilizer_cost": 7000.0,
        "labour_cost": 7000.0,
        "irrigation_other_cost": 1800.0,
        "peer_guarantors_count": 3
    })
    pooja_data = intake_pooja.json()
    pooja_id = pooja_data["farmer_id"]
    pooja_limit = pooja_data["underwriting_result"]["credit_limit"]

    res_assign_pooja = client.post("/api/v1/fpo/assign-member", json={
        "farmer_id": pooja_id,
        "group_id": new_group_id,
        "role": "MEMBER",
        "guarantee_pledged": True
    })
    assert res_assign_pooja.status_code == 200
    assert res_assign_pooja.json()["member_count"] == 3
    expected_full_limit = soha_limit + rohan_limit + pooja_limit
    assert res_assign_pooja.json()["total_pool_credit_limit"] == expected_full_limit
    print(f"[PASS] 8. Pooja Jadhav added to pool (3/3 Full). Total pool credit limit: INR{expected_full_limit:,.0f}")

    # 9. Verify attempt to add 4th member is strictly rejected
    amit_phone = f"886679{int(time.time()) % 10000:04d}"
    intake_amit = client.post("/api/v1/underwriting/submit-application", json={
        "farmer_name": "Amit Shinde",
        "phone": amit_phone,
        "village": "Pimpalgaon",
        "district": "Nashik",
        "crop_name": "Tomato (Horticulture)",
        "acres": 2.0,
        "projected_yield": 18.0,
        "seeds_cost": 6000.0,
        "fertilizer_cost": 8000.0,
        "labour_cost": 8000.0,
        "irrigation_other_cost": 2000.0,
        "peer_guarantors_count": 3
    })
    amit_id = intake_amit.json()["farmer_id"]

    res_overflow2 = client.post("/api/v1/fpo/assign-member", json={
        "farmer_id": amit_id,
        "group_id": new_group_id,
        "role": "MEMBER",
        "guarantee_pledged": True
    })
    assert res_overflow2.status_code == 400
    print(f"[PASS] 9. Strict 3-member ceiling enforced: 4th member assignment rejected")

    # 10. Test Direct Pool Linking on Intake (Option A)
    # 10a. Intake with FULL pool specified -> safely marks POOL_FULL_UNASSIGNED
    direct_phone = f"886680{int(time.time()) % 10000:04d}"
    res_direct_full = client.post("/api/v1/underwriting/submit-application", json={
        "farmer_name": "Vikram Rathore",
        "phone": direct_phone,
        "village": "Pimpalgaon",
        "district": "Nashik",
        "target_pool_id": new_group_id, # This pool is already full at 3/3!
        "crop_name": "Tomato (Horticulture)",
        "acres": 2.0,
        "projected_yield": 18.0,
        "seeds_cost": 6000.0,
        "fertilizer_cost": 8000.0,
        "labour_cost": 8000.0,
        "irrigation_other_cost": 2000.0,
        "peer_guarantors_count": 3
    })
    direct_full_data = res_direct_full.json()
    assert direct_full_data["pool_assignment"]["status"] == "POOL_FULL_UNASSIGNED"
    print(f"[PASS] 10a. Intake with full pool choice marks farmer as POOL_FULL_UNASSIGNED without violating 3-member rule")

    # 10b. Create an open forming pool with 1 member (Amit)
    open_pool_code = f"GRP-OPEN-{int(time.time()) % 10000}"
    res_op = client.post("/api/v1/fpo/groups", json={
        "group_code": open_pool_code,
        "fpo_name": "Sahyadri Agro Producer Co.",
        "village": "Pimpalgaon",
        "district": "Nashik",
        "member_farmer_ids": [amit_id]
    })
    assert res_op.status_code == 201
    open_pool_id = res_op.json()["group_id"]

    # Intake with open pool specified -> links directly
    kavita_phone = f"886681{int(time.time()) % 10000:04d}"
    res_direct_open = client.post("/api/v1/underwriting/submit-application", json={
        "farmer_name": "Kavita Shinde",
        "phone": kavita_phone,
        "village": "Pimpalgaon",
        "district": "Nashik",
        "target_pool_id": open_pool_id, # This pool has 1/3 members!
        "crop_name": "Tomato (Horticulture)",
        "acres": 1.5,
        "projected_yield": 18.0,
        "seeds_cost": 5000.0,
        "fertilizer_cost": 6000.0,
        "labour_cost": 6000.0,
        "irrigation_other_cost": 1500.0,
        "peer_guarantors_count": 3
    })
    direct_open_data = res_direct_open.json()
    assert direct_open_data["pool_assignment"]["status"] == "ASSIGNED"
    assert direct_open_data["pool_assignment"]["pool_id"] == open_pool_id
    print(f"[PASS] 10b. Intake with open pool choice directly links farmer to pool ({open_pool_code})")

    print("==================================================================")
    print("  ALL 10 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    run_integration_tests()
