"""
Fire Resistance Testing Protocol - Data Models
IEC 61730-2 MST 23

This module defines the data models for fire resistance testing including
test samples, measurements, results, and reporting structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class TestStatus(Enum):
    """Test execution status enumeration"""
    RECEIVED = "Received"
    IN_CONDITIONING = "In Conditioning"
    READY_FOR_TEST = "Ready for Test"
    TESTING_IN_PROGRESS = "Testing in Progress"
    TEST_COMPLETE = "Test Complete"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    ARCHIVED = "Archived"


class PassFailResult(Enum):
    """Test result enumeration"""
    PASS = "Pass"
    FAIL = "Fail"
    CONDITIONAL = "Conditional"
    PENDING = "Pending"


class SmokeLevel(Enum):
    """Smoke generation level"""
    NONE = "None"
    LIGHT = "Light"
    MODERATE = "Moderate"
    HEAVY = "Heavy"


class MaterialIntegrity(Enum):
    """Material integrity assessment"""
    INTACT = "Intact"
    MINOR_DAMAGE = "Minor Damage"
    MODERATE_DAMAGE = "Moderate Damage"
    SEVERE_DAMAGE = "Severe Damage"
    FAILURE = "Failure"


@dataclass
class SampleInformation:
    """PV Module sample information"""
    sample_id: str
    manufacturer: str
    model_number: str
    serial_number: str
    date_of_manufacture: Optional[str] = None
    batch_number: Optional[str] = None
    receipt_date: Optional[datetime] = None
    visual_condition: str = "Good"
    dimensions: Dict[str, float] = field(default_factory=dict)
    weight_kg: Optional[float] = None
    pre_test_photos: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'sample_id': self.sample_id,
            'manufacturer': self.manufacturer,
            'model_number': self.model_number,
            'serial_number': self.serial_number,
            'date_of_manufacture': self.date_of_manufacture,
            'batch_number': self.batch_number,
            'receipt_date': self.receipt_date.isoformat() if self.receipt_date else None,
            'visual_condition': self.visual_condition,
            'dimensions': self.dimensions,
            'weight_kg': self.weight_kg,
            'pre_test_photos': self.pre_test_photos
        }


@dataclass
class EnvironmentalConditions:
    """Test environmental conditions"""
    temperature_c: float
    relative_humidity: float
    atmospheric_pressure_kpa: Optional[float] = None
    conditioning_start: Optional[datetime] = None
    conditioning_end: Optional[datetime] = None

    def is_within_spec(self) -> bool:
        """Check if conditions meet specification (23±5°C, 50±20% RH)"""
        temp_ok = 18 <= self.temperature_c <= 28
        humidity_ok = 30 <= self.relative_humidity <= 70
        return temp_ok and humidity_ok

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'temperature_c': self.temperature_c,
            'relative_humidity': self.relative_humidity,
            'atmospheric_pressure_kpa': self.atmospheric_pressure_kpa,
            'conditioning_start': self.conditioning_start.isoformat() if self.conditioning_start else None,
            'conditioning_end': self.conditioning_end.isoformat() if self.conditioning_end else None,
            'within_spec': self.is_within_spec()
        }


@dataclass
class EquipmentCalibration:
    """Equipment calibration record"""
    equipment_id: str
    equipment_name: str
    calibration_date: datetime
    calibration_due_date: datetime
    calibration_certificate: str
    calibrated_by: str
    is_valid: bool = True

    def check_validity(self) -> bool:
        """Check if calibration is still valid"""
        self.is_valid = datetime.now() <= self.calibration_due_date
        return self.is_valid

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment_name,
            'calibration_date': self.calibration_date.isoformat(),
            'calibration_due_date': self.calibration_due_date.isoformat(),
            'calibration_certificate': self.calibration_certificate,
            'calibrated_by': self.calibrated_by,
            'is_valid': self.check_validity()
        }


@dataclass
class RealTimeMeasurement:
    """Real-time measurement data point"""
    timestamp: datetime
    elapsed_time_seconds: float
    surface_temperature_c: float
    flame_spread_mm: Optional[float] = None
    observations: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'elapsed_time_seconds': self.elapsed_time_seconds,
            'surface_temperature_c': self.surface_temperature_c,
            'flame_spread_mm': self.flame_spread_mm,
            'observations': self.observations
        }


@dataclass
class TestObservations:
    """Test observations and qualitative data"""
    ignition_occurred: bool = False
    time_to_ignition_seconds: Optional[float] = None
    self_extinguishing: bool = False
    self_extinguishing_time_seconds: Optional[float] = None
    dripping_materials: bool = False
    flaming_drips: bool = False
    smoke_generation: SmokeLevel = SmokeLevel.NONE
    material_integrity: MaterialIntegrity = MaterialIntegrity.INTACT
    max_flame_spread_mm: float = 0.0
    burning_duration_seconds: float = 0.0
    continued_smoldering: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'ignition_occurred': self.ignition_occurred,
            'time_to_ignition_seconds': self.time_to_ignition_seconds,
            'self_extinguishing': self.self_extinguishing,
            'self_extinguishing_time_seconds': self.self_extinguishing_time_seconds,
            'dripping_materials': self.dripping_materials,
            'flaming_drips': self.flaming_drips,
            'smoke_generation': self.smoke_generation.value,
            'material_integrity': self.material_integrity.value,
            'max_flame_spread_mm': self.max_flame_spread_mm,
            'burning_duration_seconds': self.burning_duration_seconds,
            'continued_smoldering': self.continued_smoldering,
            'notes': self.notes
        }


@dataclass
class AcceptanceCriteriaResult:
    """Individual acceptance criterion evaluation"""
    criterion_name: str
    requirement: str
    measured_value: Any
    pass_condition: str
    result: PassFailResult
    severity: str  # "critical" or "major"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'criterion_name': self.criterion_name,
            'requirement': self.requirement,
            'measured_value': self.measured_value,
            'pass_condition': self.pass_condition,
            'result': self.result.value,
            'severity': self.severity,
            'notes': self.notes
        }


@dataclass
class TestResults:
    """Complete test results"""
    test_id: str
    sample: SampleInformation
    test_date: datetime
    test_personnel: List[str]
    environmental_conditions: EnvironmentalConditions
    equipment_used: List[EquipmentCalibration]
    real_time_data: List[RealTimeMeasurement]
    observations: TestObservations
    acceptance_results: List[AcceptanceCriteriaResult]
    overall_result: PassFailResult
    post_test_photos: List[str] = field(default_factory=list)
    test_duration_minutes: Optional[float] = None

    def evaluate_acceptance_criteria(self) -> PassFailResult:
        """Evaluate all acceptance criteria and determine overall result"""
        # Check critical criteria
        critical_failures = [
            r for r in self.acceptance_results
            if r.severity == "critical" and r.result == PassFailResult.FAIL
        ]

        if critical_failures:
            self.overall_result = PassFailResult.FAIL
            return PassFailResult.FAIL

        # Check major criteria
        major_failures = [
            r for r in self.acceptance_results
            if r.severity == "major" and r.result == PassFailResult.FAIL
        ]

        if major_failures:
            self.overall_result = PassFailResult.CONDITIONAL
            return PassFailResult.CONDITIONAL

        self.overall_result = PassFailResult.PASS
        return PassFailResult.PASS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'test_id': self.test_id,
            'sample': self.sample.to_dict(),
            'test_date': self.test_date.isoformat(),
            'test_personnel': self.test_personnel,
            'environmental_conditions': self.environmental_conditions.to_dict(),
            'equipment_used': [eq.to_dict() for eq in self.equipment_used],
            'real_time_data': [m.to_dict() for m in self.real_time_data],
            'observations': self.observations.to_dict(),
            'acceptance_results': [r.to_dict() for r in self.acceptance_results],
            'overall_result': self.overall_result.value,
            'post_test_photos': self.post_test_photos,
            'test_duration_minutes': self.test_duration_minutes
        }

    def to_json(self, filepath: Optional[str] = None) -> str:
        """Export to JSON format"""
        data = self.to_dict()
        json_str = json.dumps(data, indent=2)

        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)

        return json_str


@dataclass
class TestReport:
    """Complete test report structure"""
    report_id: str
    protocol_id: str = "FIRE-001"
    protocol_version: str = "1.0.0"
    results: TestResults = None
    executive_summary: str = ""
    analysis: str = ""
    conclusion: str = ""
    recommendations: List[str] = field(default_factory=list)
    report_date: datetime = field(default_factory=datetime.now)
    prepared_by: str = ""
    reviewed_by: str = ""
    approved_by: str = ""
    signatures: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def generate_executive_summary(self) -> str:
        """Auto-generate executive summary"""
        if not self.results:
            return "No test results available"

        summary = f"""
Fire Resistance Testing - Executive Summary
Test ID: {self.results.test_id}
Sample: {self.results.sample.manufacturer} {self.results.sample.model_number}
Serial Number: {self.results.sample.serial_number}
Test Date: {self.results.test_date.strftime('%Y-%m-%d')}

Overall Result: {self.results.overall_result.value}

Key Findings:
- Ignition: {'Yes' if self.results.observations.ignition_occurred else 'No'}
- Self-Extinguishing: {'Yes' if self.results.observations.self_extinguishing else 'No'}
- Maximum Flame Spread: {self.results.observations.max_flame_spread_mm} mm
- Flaming Drips: {'Yes' if self.results.observations.flaming_drips else 'No'}
- Material Integrity: {self.results.observations.material_integrity.value}
"""
        self.executive_summary = summary.strip()
        return self.executive_summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'report_id': self.report_id,
            'protocol_id': self.protocol_id,
            'protocol_version': self.protocol_version,
            'results': self.results.to_dict() if self.results else None,
            'executive_summary': self.executive_summary,
            'analysis': self.analysis,
            'conclusion': self.conclusion,
            'recommendations': self.recommendations,
            'report_date': self.report_date.isoformat(),
            'prepared_by': self.prepared_by,
            'reviewed_by': self.reviewed_by,
            'approved_by': self.approved_by,
            'signatures': self.signatures
        }

    def export_to_json(self, filepath: str) -> None:
        """Export report to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def export_to_csv(self, filepath: str) -> None:
        """Export measurement data to CSV"""
        import csv

        if not self.results or not self.results.real_time_data:
            return

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp',
                'Elapsed Time (s)',
                'Surface Temperature (°C)',
                'Flame Spread (mm)',
                'Observations'
            ])

            for measurement in self.results.real_time_data:
                writer.writerow([
                    measurement.timestamp.isoformat(),
                    measurement.elapsed_time_seconds,
                    measurement.surface_temperature_c,
                    measurement.flame_spread_mm or '',
                    measurement.observations
                ])
