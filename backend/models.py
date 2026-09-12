from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.database import Base


class FarmerStatus(str, enum.Enum):
    """Farmer account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class Farmer(Base):
    """Farmer model representing marginal farmers"""
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    village = Column(String(255), nullable=False)
    district = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    land_size_acres = Column(Float, nullable=False)
    status = Column(SQLEnum(FarmerStatus), default=FarmerStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    credit_assessments = relationship("CreditAssessment", back_populates="farmer")

    def __repr__(self):
        return f"<Farmer(id={self.id}, name={self.name}, phone={self.phone})>"


class CreditAssessment(Base):
    """Credit assessment model for farmers"""
    __tablename__ = "credit_assessments"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    credit_score = Column(Integer, nullable=False)
    loan_eligibility_amount = Column(Float, nullable=False)
    risk_category = Column(String(50), nullable=False)
    notes = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    farmer = relationship("Farmer", back_populates="credit_assessments")

    def __repr__(self):
        return f"<CreditAssessment(id={self.id}, farmer_id={self.farmer_id}, score={self.credit_score})>"
