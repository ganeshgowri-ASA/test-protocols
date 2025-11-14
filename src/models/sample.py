"""
Sample Model

Data model for test samples/specimens.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base import BaseModel


@dataclass
class Sample(BaseModel):
    """
    Sample/specimen data model.

    Represents a physical sample being tested.
    """

    sample_id: str
    material_type: str
    dimensions: Dict[str, float] = field(default_factory=dict)  # length, width, thickness
    batch_code: Optional[str] = None
    lot_number: Optional[str] = None
    manufacturer: Optional[str] = None
    manufacturing_date: Optional[datetime] = None
    baseline_measurements: Dict[str, float] = field(default_factory=dict)
    storage_conditions: Dict[str, Any] = field(default_factory=dict)
    preparation_notes: Optional[str] = None
    source_batch_id: Optional[str] = None
    sample_location: Optional[str] = None  # Storage or test location
    status: str = "AVAILABLE"  # AVAILABLE, IN_TEST, TESTED, CONSUMED, ARCHIVED
    metadata: Dict[str, Any] = field(default_factory=dict)

    def set_baseline(self, parameter: str, value: float):
        """
        Set a baseline measurement value.

        Args:
            parameter: Parameter name (e.g., 'yellow_index')
            value: Baseline value
        """
        self.baseline_measurements[parameter] = value
        self.update()

    def get_baseline(self, parameter: str) -> Optional[float]:
        """
        Get a baseline measurement value.

        Args:
            parameter: Parameter name

        Returns:
            Baseline value or None if not set
        """
        return self.baseline_measurements.get(parameter)

    def has_baseline(self) -> bool:
        """Check if baseline measurements have been taken."""
        return len(self.baseline_measurements) > 0

    def mark_in_test(self):
        """Mark sample as currently in testing."""
        self.status = "IN_TEST"
        self.update()

    def mark_tested(self):
        """Mark sample as tested."""
        self.status = "TESTED"
        self.update()

    def get_dimension(self, dimension: str) -> Optional[float]:
        """
        Get a specific dimension.

        Args:
            dimension: Dimension name (e.g., 'length_mm')

        Returns:
            Dimension value or None
        """
        return self.dimensions.get(dimension)

    def calculate_area_mm2(self) -> Optional[float]:
        """
        Calculate sample area from dimensions.

        Returns:
            Area in mm² or None if dimensions not available
        """
        length = self.dimensions.get('length_mm')
        width = self.dimensions.get('width_mm')

        if length and width:
            return length * width

        return None

    def calculate_volume_mm3(self) -> Optional[float]:
        """
        Calculate sample volume from dimensions.

        Returns:
            Volume in mm³ or None if dimensions not available
        """
        area = self.calculate_area_mm2()
        thickness = self.dimensions.get('thickness_mm')

        if area and thickness:
            return area * thickness

        return None


@dataclass
class SampleBatch(BaseModel):
    """
    Sample batch data model.

    Represents a batch of samples from the same source.
    """

    batch_id: str
    batch_code: str
    material_type: str
    manufacturer: Optional[str] = None
    manufacturing_date: Optional[datetime] = None
    received_date: Optional[datetime] = None
    sample_ids: List[str] = field(default_factory=list)
    quantity: int = 0
    batch_properties: Dict[str, Any] = field(default_factory=dict)
    quality_certificate: Optional[str] = None  # Path or reference to QC cert
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_sample(self, sample_id: str):
        """
        Add a sample to the batch.

        Args:
            sample_id: Sample identifier
        """
        if sample_id not in self.sample_ids:
            self.sample_ids.append(sample_id)
            self.quantity = len(self.sample_ids)
            self.update()

    def remove_sample(self, sample_id: str):
        """
        Remove a sample from the batch.

        Args:
            sample_id: Sample identifier
        """
        if sample_id in self.sample_ids:
            self.sample_ids.remove(sample_id)
            self.quantity = len(self.sample_ids)
            self.update()

    def get_sample_count(self) -> int:
        """Get number of samples in batch."""
        return len(self.sample_ids)
