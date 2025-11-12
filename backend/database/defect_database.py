"""
Defect Database Schema and Integration
Centralized database for storing and querying defect data with traceability
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DefectCategory(Enum):
    """Main defect categories"""
    STRUCTURAL = "structural"
    ELECTRICAL = "electrical"
    THERMAL = "thermal"
    MATERIAL_DEGRADATION = "material_degradation"
    COSMETIC = "cosmetic"


class SeverityLevel(Enum):
    """Defect severity levels"""
    CRITICAL = 5
    SEVERE = 4
    MODERATE = 3
    MINOR = 2
    COSMETIC = 1


class ReviewStatus(Enum):
    """Defect review status"""
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_INVESTIGATION = "under_investigation"


@dataclass
class DefectRecord:
    """Complete defect record"""
    # Primary identification
    defect_id: str
    module_serial: str
    test_id: str

    # Defect classification
    defect_category: DefectCategory
    defect_type: str
    defect_subtype: Optional[str]
    severity_level: SeverityLevel

    # Detection information
    detection_method: str  # EL, IR, Visual, UV, PL
    detection_timestamp: datetime
    ai_model_version: Optional[str]
    confidence: float

    # Spatial information
    location_coordinates: Dict[str, float]  # {x, y, z}
    bounding_box: Dict[str, int]  # {x, y, width, height}
    area_pixels: int
    area_mm2: Optional[float]

    # Quantitative metrics
    quantitative_metrics: Dict[str, Any]  # Flexible metrics storage

    # Impact assessment
    power_loss_estimate: Optional[float]  # Percentage
    safety_risk: bool
    propagation_risk: Optional[str]  # low, medium, high

    # Associated data
    image_paths: Dict[str, str]  # {raw, processed, annotated}
    associated_test_ids: List[str]  # Related test IDs

    # Review and workflow
    review_status: ReviewStatus
    reviewer_id: Optional[str]
    review_notes: Optional[str]
    corrective_action: Optional[str]
    nc_number: Optional[str]  # Non-conformance number if applicable

    # Metadata
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert enums to values
        data['defect_category'] = self.defect_category.value
        data['severity_level'] = self.severity_level.value
        data['review_status'] = self.review_status.value
        # Convert timestamps
        data['detection_timestamp'] = self.detection_timestamp.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'DefectRecord':
        """Create from dictionary"""
        # Convert enums
        data['defect_category'] = DefectCategory(data['defect_category'])
        data['severity_level'] = SeverityLevel(data['severity_level'])
        data['review_status'] = ReviewStatus(data['review_status'])
        # Convert timestamps
        data['detection_timestamp'] = datetime.fromisoformat(data['detection_timestamp'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class ModuleSummary:
    """Summary of all defects for a module"""
    module_serial: str
    total_defects: int
    defects_by_category: Dict[str, int]
    defects_by_severity: Dict[str, int]
    overall_grade: str
    qc_status: str
    nc_raised: bool
    total_power_loss_estimate: float
    critical_issues: List[str]
    last_inspection_date: datetime


class DefectDatabase:
    """Database interface for defect management"""

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database connection

        Args:
            connection_string: Database connection string
        """
        self.connection_string = connection_string
        self.logger = logging.getLogger(self.__class__.__name__)

        # In-memory storage for demo (replace with actual database)
        self._defects: Dict[str, DefectRecord] = {}
        self._modules: Dict[str, ModuleSummary] = {}

    def insert_defect(self, defect: DefectRecord) -> bool:
        """
        Insert defect record into database

        Args:
            defect: Defect record to insert

        Returns:
            Success status
        """
        try:
            self._defects[defect.defect_id] = defect
            self.logger.info(f"Inserted defect: {defect.defect_id}")

            # Update module summary
            self._update_module_summary(defect.module_serial)

            return True
        except Exception as e:
            self.logger.error(f"Failed to insert defect: {e}")
            return False

    def get_defect(self, defect_id: str) -> Optional[DefectRecord]:
        """
        Retrieve defect by ID

        Args:
            defect_id: Defect ID

        Returns:
            Defect record or None
        """
        return self._defects.get(defect_id)

    def query_defects(self, **filters) -> List[DefectRecord]:
        """
        Query defects with filters

        Args:
            **filters: Filter criteria (module_serial, defect_type, severity_level, etc.)

        Returns:
            List of matching defects
        """
        results = []

        for defect in self._defects.values():
            match = True

            for key, value in filters.items():
                if hasattr(defect, key):
                    defect_value = getattr(defect, key)

                    # Handle enum comparisons
                    if isinstance(defect_value, Enum):
                        defect_value = defect_value.value

                    if defect_value != value:
                        match = False
                        break

            if match:
                results.append(defect)

        return results

    def get_module_defects(self, module_serial: str) -> List[DefectRecord]:
        """
        Get all defects for a module

        Args:
            module_serial: Module serial number

        Returns:
            List of defects
        """
        return self.query_defects(module_serial=module_serial)

    def get_module_summary(self, module_serial: str) -> Optional[ModuleSummary]:
        """
        Get defect summary for module

        Args:
            module_serial: Module serial number

        Returns:
            Module summary or None
        """
        if module_serial not in self._modules:
            self._update_module_summary(module_serial)

        return self._modules.get(module_serial)

    def update_defect_status(self, defect_id: str,
                            review_status: ReviewStatus,
                            reviewer_id: str,
                            notes: Optional[str] = None) -> bool:
        """
        Update defect review status

        Args:
            defect_id: Defect ID
            review_status: New status
            reviewer_id: Reviewer ID
            notes: Optional review notes

        Returns:
            Success status
        """
        defect = self.get_defect(defect_id)
        if defect is None:
            return False

        defect.review_status = review_status
        defect.reviewer_id = reviewer_id
        if notes:
            defect.review_notes = notes
        defect.updated_at = datetime.now()

        self.logger.info(f"Updated defect {defect_id} status to {review_status.value}")
        return True

    def _update_module_summary(self, module_serial: str):
        """Update module summary statistics"""
        defects = self.get_module_defects(module_serial)

        if not defects:
            return

        # Count by category
        by_category = {}
        for defect in defects:
            cat = defect.defect_category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        # Count by severity
        by_severity = {}
        for defect in defects:
            sev = defect.severity_level.name
            by_severity[sev] = by_severity.get(sev, 0) + 1

        # Calculate grade
        grade = self._calculate_grade(by_severity)

        # Calculate total power loss
        total_power_loss = sum(
            d.power_loss_estimate or 0.0 for d in defects
        )

        # Check for critical issues
        critical_issues = [
            d.defect_type for d in defects
            if d.severity_level == SeverityLevel.CRITICAL or d.safety_risk
        ]

        # Determine QC status
        qc_status = "FAIL" if grade in ['D', 'F'] or critical_issues else "PASS"

        # Check if NC raised
        nc_raised = any(d.nc_number is not None for d in defects)

        summary = ModuleSummary(
            module_serial=module_serial,
            total_defects=len(defects),
            defects_by_category=by_category,
            defects_by_severity=by_severity,
            overall_grade=grade,
            qc_status=qc_status,
            nc_raised=nc_raised,
            total_power_loss_estimate=total_power_loss,
            critical_issues=critical_issues,
            last_inspection_date=datetime.now()
        )

        self._modules[module_serial] = summary

    def _calculate_grade(self, severity_counts: Dict[str, int]) -> str:
        """Calculate module grade from severity counts"""
        critical = severity_counts.get('CRITICAL', 0)
        severe = severity_counts.get('SEVERE', 0)
        moderate = severity_counts.get('MODERATE', 0)
        minor = severity_counts.get('MINOR', 0)

        if critical > 0 or severe > 3:
            return 'F'
        elif severe <= 3:
            if moderate <= 2 and minor <= 5:
                if moderate == 0 and minor <= 2:
                    return 'A'
                elif moderate <= 1:
                    return 'B'
                else:
                    return 'C'
            else:
                return 'D'
        return 'F'

    def export_module_data(self, module_serial: str,
                          format: str = 'json') -> str:
        """
        Export all data for a module

        Args:
            module_serial: Module serial number
            format: Export format ('json', 'csv')

        Returns:
            Exported data string
        """
        defects = self.get_module_defects(module_serial)
        summary = self.get_module_summary(module_serial)

        if format == 'json':
            data = {
                'module_serial': module_serial,
                'summary': asdict(summary) if summary else None,
                'defects': [d.to_dict() for d in defects]
            }
            return json.dumps(data, indent=2, default=str)

        elif format == 'csv':
            # Implement CSV export
            pass

        return ""

    def get_defect_statistics(self, filters: Optional[Dict] = None) -> Dict:
        """
        Get statistical analysis of defects

        Args:
            filters: Optional filters

        Returns:
            Statistics dictionary
        """
        defects = list(self._defects.values()) if not filters else self.query_defects(**filters)

        stats = {
            'total_defects': len(defects),
            'by_category': {},
            'by_severity': {},
            'by_type': {},
            'by_detection_method': {},
            'average_confidence': 0.0,
            'modules_affected': len(set(d.module_serial for d in defects))
        }

        if not defects:
            return stats

        # Count by various dimensions
        for defect in defects:
            # Category
            cat = defect.defect_category.value
            stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1

            # Severity
            sev = defect.severity_level.name
            stats['by_severity'][sev] = stats['by_severity'].get(sev, 0) + 1

            # Type
            dtype = defect.defect_type
            stats['by_type'][dtype] = stats['by_type'].get(dtype, 0) + 1

            # Detection method
            method = defect.detection_method
            stats['by_detection_method'][method] = stats['by_detection_method'].get(method, 0) + 1

        # Average confidence
        stats['average_confidence'] = sum(d.confidence for d in defects) / len(defects)

        return stats


class LIMSIntegration:
    """Integration with Laboratory Information Management System"""

    def __init__(self, lims_url: str, api_key: str):
        self.lims_url = lims_url
        self.api_key = api_key
        self.logger = logging.getLogger(self.__class__.__name__)

    def sync_defect(self, defect: DefectRecord) -> bool:
        """Sync defect to LIMS"""
        # Placeholder for LIMS API call
        self.logger.info(f"Syncing defect {defect.defect_id} to LIMS")
        return True

    def sync_module_results(self, module_serial: str, summary: ModuleSummary) -> bool:
        """Sync module test results to LIMS"""
        self.logger.info(f"Syncing module {module_serial} results to LIMS")
        return True


class QMSIntegration:
    """Integration with Quality Management System"""

    def __init__(self, qms_url: str, api_key: str):
        self.qms_url = qms_url
        self.api_key = api_key
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_nc(self, defect: DefectRecord) -> Optional[str]:
        """
        Create non-conformance in QMS

        Args:
            defect: Defect triggering NC

        Returns:
            NC number or None
        """
        # Placeholder for QMS API call
        nc_number = f"NC-{defect.defect_id}"
        self.logger.info(f"Created NC: {nc_number}")
        return nc_number

    def update_nc(self, nc_number: str, status: str, notes: str) -> bool:
        """Update NC status in QMS"""
        self.logger.info(f"Updated NC {nc_number}: {status}")
        return True


# Global database instance
defect_db = DefectDatabase()


if __name__ == "__main__":
    print("Defect Database System initialized")
    print(f"Defect categories: {[c.value for c in DefectCategory]}")
    print(f"Severity levels: {[s.name for s in SeverityLevel]}")
