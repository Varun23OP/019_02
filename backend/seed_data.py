"""
Seed initial demo data for KisanSetu:
- 2 FPO Peer Guarantee Groups (Sahyadri Agro Producer Co. and Tapi Valley Organic FPO)
- 6 Marginal Farmers (< 2.5 acres each, zero land deeds)
- Mutual social collateral pledges
- Verified field crop inspection records
"""

from datetime import datetime, timedelta
from backend.database import SessionLocal, engine, Base
from backend.models import Farmer, FarmerStatus, PeerGroup, PeerGroupMember, CropVerification, CreditAssessment
import json


def seed_database():
    db = SessionLocal()
    try:
        # Clear existing data
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        # 1. Create Peer Group 1 (Nashik, Tomato)
        group1 = PeerGroup(
            group_code="GRP-SAHYADRI-01",
            fpo_name="Sahyadri Agro Producer Co.",
            village="Pimpalgaon",
            district="Nashik",
            status="ACTIVE",
            repayment_rate=100.0
        )
        db.add(group1)
        db.commit()
        db.refresh(group1)

        # 2. Create Farmers for Group 1
        farmer1 = Farmer(
            name="Ramesh Patel",
            phone="9876543210",
            village="Pimpalgaon",
            district="Nashik",
            state="Maharashtra",
            land_size_acres=2.0,
            status=FarmerStatus.ACTIVE
        )
        farmer2 = Farmer(
            name="Suresh Kumar",
            phone="9876543212",
            village="Pimpalgaon",
            district="Nashik",
            state="Maharashtra",
            land_size_acres=1.8,
            status=FarmerStatus.ACTIVE
        )
        farmer3 = Farmer(
            name="Dinesh Bhai",
            phone="9876543213",
            village="Pimpalgaon",
            district="Nashik",
            state="Maharashtra",
            land_size_acres=2.2,
            status=FarmerStatus.ACTIVE
        )
        db.add_all([farmer1, farmer2, farmer3])
        db.commit()
        db.refresh(farmer1)
        db.refresh(farmer2)
        db.refresh(farmer3)

        # Add to Group 1
        db.add(PeerGroupMember(group_id=group1.id, farmer_id=farmer1.id, role="LEADER", guarantee_pledged=True))
        db.add(PeerGroupMember(group_id=group1.id, farmer_id=farmer2.id, role="MEMBER", guarantee_pledged=True))
        db.add(PeerGroupMember(group_id=group1.id, farmer_id=farmer3.id, role="MEMBER", guarantee_pledged=True))
        db.commit()

        # Crop Verification for Farmer 1
        ver1 = CropVerification(
            farmer_id=farmer1.id,
            crop_name="Tomato (Horticulture)",
            verified_acres=2.0,
            crop_stage="Vegetative (Flowering)",
            sowing_date=datetime.now() - timedelta(days=35),
            expected_harvest_date=datetime.now() + timedelta(days=75),
            field_officer_name="Anand Shinde (Sahyadri FPO)",
            verification_status="VERIFIED",
            geo_lat=20.1745,
            geo_lng=73.9872,
            notes="Drip irrigation installed. Healthy tomato saplings with zero pest infestation."
        )
        db.add(ver1)
        db.commit()

        # 3. Create Peer Group 2 (Indore, Soybean)
        group2 = PeerGroup(
            group_code="GRP-TAPI-02",
            fpo_name="Tapi Valley Organic FPO",
            village="Depalpur",
            district="Indore",
            status="ACTIVE",
            repayment_rate=100.0
        )
        db.add(group2)
        db.commit()
        db.refresh(group2)

        farmer4 = Farmer(
            name="Geeta Devi",
            phone="9876543211",
            village="Depalpur",
            district="Indore",
            state="Madhya Pradesh",
            land_size_acres=1.5,
            status=FarmerStatus.ACTIVE
        )
        farmer5 = Farmer(
            name="Jayesh Vora",
            phone="9876543214",
            village="Depalpur",
            district="Indore",
            state="Madhya Pradesh",
            land_size_acres=2.0,
            status=FarmerStatus.ACTIVE
        )
        farmer6 = Farmer(
            name="Govind Solanki",
            phone="9876543215",
            village="Depalpur",
            district="Indore",
            state="Madhya Pradesh",
            land_size_acres=1.5,
            status=FarmerStatus.ACTIVE
        )
        db.add_all([farmer4, farmer5, farmer6])
        db.commit()
        db.refresh(farmer4)
        db.refresh(farmer5)
        db.refresh(farmer6)

        db.add(PeerGroupMember(group_id=group2.id, farmer_id=farmer4.id, role="LEADER", guarantee_pledged=True))
        db.add(PeerGroupMember(group_id=group2.id, farmer_id=farmer5.id, role="MEMBER", guarantee_pledged=True))
        db.add(PeerGroupMember(group_id=group2.id, farmer_id=farmer6.id, role="MEMBER", guarantee_pledged=True))
        db.commit()

        # Crop Verification for Farmer 4
        ver2 = CropVerification(
            farmer_id=farmer4.id,
            crop_name="Soybean",
            verified_acres=1.5,
            crop_stage="Pod Formation",
            sowing_date=datetime.now() - timedelta(days=40),
            expected_harvest_date=datetime.now() + timedelta(days=55),
            field_officer_name="Sunil Verma (Tapi FPO)",
            verification_status="VERIFIED",
            geo_lat=22.8456,
            geo_lng=75.5412,
            notes="Crop vigorous. Yellow mosaic resistant variety verified."
        )
        db.add(ver2)
        db.commit()

        # Add Credit Assessment for Geeta Devi (Already Sanctioned)
        bullet_date_geeta = datetime.now() + timedelta(days=125)
        assessment_geeta = CreditAssessment(
            farmer_id=farmer4.id,
            assessment_date=datetime.now(),
            credit_score=82,
            loan_eligibility_amount=20817.0,
            risk_category="Tier-1 Low Risk (Preferred Agro-Credit)",
            crop_name="Soybean",
            acres=1.5,
            projected_yield=9.5,
            mandi_price_per_qtl=4720.0,
            gross_revenue=67260.0,
            total_expenses=21000.0,
            net_profit=46260.0,
            pmfby_insured=True,
            bullet_repayment_date=bullet_date_geeta,
            status="SANCTIONED",
            score_breakdown=json.dumps([
                {"factor": "Base Agronomic Foundation", "points_awarded": 35},
                {"factor": "Operating Cashflow Margin", "points_awarded": 22},
                {"factor": "FPO 3-Peer Social Guarantee", "points_awarded": 15},
                {"factor": "PMFBY Crop Insurance Protection", "points_awarded": 10}
            ]),
            lender_notes="Sanctioned under Priority Sector Lending. 3/3 Peer guarantors verified."
        )
        db.add(assessment_geeta)
        db.commit()

        print("Demo database seeded successfully with 2 Peer Groups, 6 Farmers, Verifications, and Sanctioned Loans.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
