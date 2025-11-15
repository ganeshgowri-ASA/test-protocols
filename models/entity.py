"""
Entity Model
============
Hierarchical organization structure (Company → Division → Plant → Department).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from config.database import Base


class Entity(Base):
    """Hierarchical organization entity model"""
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # Company, Division, Plant, Department
    level = Column(Integer, nullable=False)  # 1-4
    location = Column(String(200))
    code = Column(String(50), unique=True, nullable=False, index=True)

    # Hierarchical structure
    parent_id = Column(Integer, ForeignKey("entities.id"), nullable=True)
    parent = relationship("Entity", remote_side=[id], backref="children")

    # Additional information
    manager_name = Column(String(100))
    contact_email = Column(String(100))
    contact_phone = Column(String(20))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit_schedules = relationship("AuditSchedule", back_populates="auditee_entity")

    def __repr__(self):
        return f"<Entity(name='{self.name}', type='{self.type}', level={self.level})>"

    @property
    def full_path(self):
        """Get full hierarchical path"""
        if self.parent:
            return f"{self.parent.full_path} → {self.name}"
        return self.name
