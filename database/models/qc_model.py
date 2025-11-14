"""QC Review database model"""

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class QCReview(Base):
    """Quality Control review model"""

    __tablename__ = "qc_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Test execution reference
    test_execution_id = Column(
        String(100), ForeignKey("test_executions.test_execution_id"), nullable=False, index=True
    )

    # Reviewer information
    reviewer_id = Column(String(100), nullable=False)
    reviewer_name = Column(String(255))
    review_date = Column(DateTime, default=datetime.utcnow)

    # QC checklist
    calibration_verified = Column(Boolean, default=False)
    reference_scale_verified = Column(Boolean, default=False)
    tape_lot_verified = Column(Boolean, default=False)
    data_verified = Column(Boolean, default=False)
    documentation_verified = Column(Boolean, default=False)

    # Overall verification status
    all_verifications_passed = Column(Boolean, default=False)

    # QC decision
    qc_decision = Column(
        String(50), nullable=False
    )  # Approve, Approve with Comments, Reject - Retest Required, Reject - Invalid Data
    qc_notes = Column(Text)

    # Additional verification data
    verification_data_json = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Approval chain
    approved_by = Column(String(100))  # Final approver (if different from reviewer)
    approved_at = Column(DateTime)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="qc_reviews")

    def __repr__(self):
        return f"<QCReview(id={self.id}, test='{self.test_execution_id}', decision='{self.qc_decision}')>"
