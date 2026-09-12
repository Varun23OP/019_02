from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.database import Base


class FarmerStatus(str, enum.Enum):
    """Farmer account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class PeerGroup(Base):
    """3-Member Peer Guarantee Group managed by FPO Coordinator"""
    __tablename__ = "peer_groups"

    id = Column(Integer, primary_key=True, index=True)
    group_code = Column(String(50), unique=True, nullable=False, index=True)
    fpo_name = Column(String(255), nullable=False)
    village = Column(String(255), nullable=False)
    district = Column(String(255), nullable=False)
    status = Column(String(50), default="ACTIVE")
    repayment_rate = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    members = relationship("PeerGroupMember", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PeerGroup(id={self.id}, code={self.group_code}, fpo={self.fpo_name})>"


class PeerGroupMember(Base):
    """Association between Farmer and Peer Group with mutual guarantee pledge"""
    __tablename__ = "peer_group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("peer_groups.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    role = Column(String(50), default="MEMBER")  # LEADER, MEMBER
    guarantee_pledged = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    group = relationship("PeerGroup", back_populates="members")
    farmer = relationship("Farmer", back_populates="group_memberships")

    def __repr__(self):
        return f"<PeerGroupMember(group_id={self.group_id}, farmer_id={self.farmer_id})>"


class Farmer(Base):
    """Farmer model representing marginal smallholders"""
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    village = Column(String(255), nullable=False)
    district = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    land_size_acres = Column(Float, nullable=False)
    fpo_name = Column(String(255), nullable=True)
    status = Column(SQLEnum(FarmerStatus), default=FarmerStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    credit_assessments = relationship("CreditAssessment", back_populates="farmer", cascade="all, delete-orphan")
    group_memberships = relationship("PeerGroupMember", back_populates="farmer", cascade="all, delete-orphan")
    crop_verifications = relationship("CropVerification", back_populates="farmer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Farmer(id={self.id}, name={self.name}, phone={self.phone})>"


class CropVerification(Base):
    """Field crop verification records submitted by FPO coordinators"""
    __tablename__ = "crop_verifications"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    crop_name = Column(String(100), nullable=False)
    verified_acres = Column(Float, nullable=False)
    crop_stage = Column(String(100), nullable=False)  # Sowing, Vegetative, Flowering, Harvest Ready
    sowing_date = Column(DateTime, default=datetime.utcnow)
    expected_harvest_date = Column(DateTime)
    field_officer_name = Column(String(255), default="FPO Field Officer")
    verification_status = Column(String(50), default="VERIFIED")  # VERIFIED, FLAGGED, REJECTED
    geo_lat = Column(Float, nullable=True)
    geo_lng = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    farmer = relationship("Farmer", back_populates="crop_verifications")

    def __repr__(self):
        return f"<CropVerification(farmer_id={self.farmer_id}, crop={self.crop_name}, status={self.verification_status})>"


class CreditAssessment(Base):
    """Comprehensive agronomic credit assessment model for marginal farmers"""
    __tablename__ = "credit_assessments"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    credit_score = Column(Integer, nullable=False)  # 0 to 100
    loan_eligibility_amount = Column(Float, nullable=False)
    risk_category = Column(String(100), nullable=False)
    crop_name = Column(String(100), nullable=True)
    acres = Column(Float, nullable=True)
    projected_yield = Column(Float, nullable=True)
    mandi_price_per_qtl = Column(Float, nullable=True)
    gross_revenue = Column(Float, nullable=True)
    total_expenses = Column(Float, nullable=True)
    net_profit = Column(Float, nullable=True)
    pmfby_insured = Column(Boolean, default=False)
    bullet_repayment_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="PENDING_REVIEW")  # PENDING_REVIEW, SANCTIONED, REJECTED, DISBURSED, REPAID
    score_breakdown = Column(Text, nullable=True)  # JSON text
    lender_notes = Column(Text, nullable=True)
    notes = Column(String(1000), nullable=True)
    disbursement_tx_id = Column(String(100), nullable=True)
    disbursed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    farmer = relationship("Farmer", back_populates="credit_assessments")

    def __repr__(self):
        return f"<CreditAssessment(id={self.id}, farmer_id={self.farmer_id}, score={self.credit_score}, limit={self.loan_eligibility_amount})>"
