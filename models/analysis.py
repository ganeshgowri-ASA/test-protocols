"""
Analysis result database models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class AnalysisResult(BaseModel):
    """EL analysis result model"""

    __tablename__ = 'analysis_results'

    test_id = Column(Integer, ForeignKey('test_executions.id'), nullable=False, index=True)
    analysis_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    analysis_type = Column(String(50), nullable=False)  # el_imaging, thermal, visual, etc.

    # Image information
    image_filename = Column(String(255))
    image_path = Column(String(500))
    image_format = Column(String(20))
    image_resolution = Column(JSON)  # width, height
    image_bit_depth = Column(Integer)

    # Analysis results
    delamination_detected = Column(Boolean, nullable=False, default=False)
    delamination_area_percent = Column(Float)
    defect_count = Column(Integer, default=0)
    severity_level = Column(String(20))  # none, minor, moderate, severe, critical

    # Module area information
    total_module_area = Column(Float)  # mm²
    affected_area = Column(Float)  # mm²

    # Quality metrics
    image_quality_score = Column(Float)
    quality_metrics = Column(JSON)  # sharpness, contrast, noise, etc.

    # Analysis parameters used
    analysis_parameters = Column(JSON)

    # Additional data
    summary = Column(Text)
    metadata = Column(JSON)

    # Relationships
    test = relationship("TestExecution", back_populates="analyses")
    defect_regions = relationship("DefectRegion", back_populates="analysis", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<AnalysisResult(id={self.id}, type='{self.analysis_type}', "
            f"delamination={self.delamination_detected})>"
        )


class DefectRegion(BaseModel):
    """Defect region model"""

    __tablename__ = 'defect_regions'

    analysis_id = Column(Integer, ForeignKey('analysis_results.id'), nullable=False, index=True)

    # Location and size
    x = Column(Integer, nullable=False)  # Top-left x coordinate
    y = Column(Integer, nullable=False)  # Top-left y coordinate
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    area = Column(Float, nullable=False)  # mm²

    # Defect characteristics
    severity = Column(String(20))  # minor, moderate, severe, critical
    defect_type = Column(String(50))  # delamination, crack, hotspot, etc.

    # Centroid
    centroid_x = Column(Float)
    centroid_y = Column(Float)

    # Intensity metrics
    intensity_mean = Column(Float)
    intensity_std = Column(Float)
    intensity_min = Column(Float)
    intensity_max = Column(Float)

    # Additional properties
    properties = Column(JSON)  # Additional defect properties
    metadata = Column(JSON)

    # Relationships
    analysis = relationship("AnalysisResult", back_populates="defect_regions")

    def __repr__(self):
        return (
            f"<DefectRegion(id={self.id}, type='{self.defect_type}', "
            f"area={self.area}, severity='{self.severity}')>"
        )
