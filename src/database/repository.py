"""Repository layer for database operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from .models import Protocol, Measurement, AnalysisResult, AuditLog, Equipment, StatusEnum


class ProtocolRepository:
    """Repository for Protocol operations."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def create_from_json(self, protocol_data: Dict[str, Any]) -> Protocol:
        """Create a Protocol instance from JSON data.

        Args:
            protocol_data: Protocol JSON dictionary

        Returns:
            Created Protocol instance
        """
        protocol_info = protocol_data.get("protocol_info", {})
        sample_info = protocol_data.get("sample_info", {})
        test_config = protocol_data.get("test_configuration", {})

        # Create protocol
        protocol = Protocol(
            protocol_id=protocol_info.get("protocol_id", "IAM-001"),
            protocol_version=protocol_info.get("protocol_version", "1.0.0"),
            test_date=datetime.fromisoformat(protocol_info.get("test_date", "").replace("Z", "+00:00"))
                       if protocol_info.get("test_date") else datetime.utcnow(),
            sample_id=sample_info.get("sample_id", ""),
            module_type=sample_info.get("module_type"),
            manufacturer=sample_info.get("manufacturer"),
            serial_number=sample_info.get("serial_number"),
            technology=sample_info.get("technology"),
            rated_power=sample_info.get("rated_power"),
            area=sample_info.get("area"),
            test_config=test_config,
            operator=protocol_info.get("operator"),
            facility=protocol_info.get("facility"),
            metadata_json=protocol_data.get("metadata"),
            status=StatusEnum.CREATED
        )

        self.session.add(protocol)
        self.session.flush()  # Get the ID

        # Create measurements
        for meas_data in protocol_data.get("measurements", []):
            measurement = Measurement(
                protocol_id=protocol.id,
                angle=meas_data.get("angle", 0),
                isc=meas_data.get("isc", 0),
                voc=meas_data.get("voc", 0),
                pmax=meas_data.get("pmax", 0),
                imp=meas_data.get("imp"),
                vmp=meas_data.get("vmp"),
                ff=meas_data.get("ff"),
                irradiance_actual=meas_data.get("irradiance_actual"),
                temperature_actual=meas_data.get("temperature_actual"),
                timestamp=datetime.fromisoformat(meas_data.get("timestamp", "").replace("Z", "+00:00"))
                          if meas_data.get("timestamp") else datetime.utcnow()
            )
            self.session.add(measurement)

        # Create analysis results if available
        if "analysis_results" in protocol_data:
            self._create_analysis_results(protocol.id, protocol_data["analysis_results"])

        return protocol

    def _create_analysis_results(
        self,
        protocol_id: int,
        analysis_data: Dict[str, Any]
    ) -> None:
        """Create analysis results entries.

        Args:
            protocol_id: Protocol ID
            analysis_data: Analysis results dictionary
        """
        fitting_params = analysis_data.get("fitting_parameters", {})

        analysis_result = AnalysisResult(
            protocol_id=protocol_id,
            analysis_type="iam_analysis",
            model_name=fitting_params.get("model"),
            parameters=fitting_params.get("parameters"),
            r_squared=fitting_params.get("r_squared"),
            rmse=fitting_params.get("rmse"),
            mae=fitting_params.get("mae"),
            iam_curve=analysis_data.get("iam_curve"),
            fit_quality=analysis_data.get("quality_metrics", {}).get("fit_quality"),
            measurement_stability=analysis_data.get("quality_metrics", {}).get("measurement_stability"),
            data_completeness=analysis_data.get("quality_metrics", {}).get("data_completeness"),
            statistics=analysis_data.get("statistics")
        )

        self.session.add(analysis_result)

    def get_by_id(self, protocol_id: int) -> Optional[Protocol]:
        """Get protocol by ID.

        Args:
            protocol_id: Protocol ID

        Returns:
            Protocol instance or None
        """
        return self.session.query(Protocol).filter(Protocol.id == protocol_id).first()

    def get_by_sample_id(self, sample_id: str) -> List[Protocol]:
        """Get all protocols for a sample.

        Args:
            sample_id: Sample ID

        Returns:
            List of Protocol instances
        """
        return self.session.query(Protocol).filter(
            Protocol.sample_id == sample_id
        ).order_by(desc(Protocol.test_date)).all()

    def get_recent(self, limit: int = 10) -> List[Protocol]:
        """Get recent protocols.

        Args:
            limit: Maximum number of protocols to return

        Returns:
            List of Protocol instances
        """
        return self.session.query(Protocol).order_by(
            desc(Protocol.created_at)
        ).limit(limit).all()

    def update_status(
        self,
        protocol_id: int,
        status: StatusEnum,
        user: Optional[str] = None
    ) -> None:
        """Update protocol status.

        Args:
            protocol_id: Protocol ID
            status: New status
            user: User making the change
        """
        protocol = self.get_by_id(protocol_id)
        if protocol:
            old_status = protocol.status
            protocol.status = status

            if status == StatusEnum.COMPLETED:
                protocol.completed_at = datetime.utcnow()

            # Log the change
            self._log_audit(
                protocol_id,
                "status_change",
                f"Status changed from {old_status.value} to {status.value}",
                user=user,
                changes={"old_status": old_status.value, "new_status": status.value}
            )

    def _log_audit(
        self,
        protocol_id: int,
        event_type: str,
        description: str,
        user: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create an audit log entry.

        Args:
            protocol_id: Protocol ID
            event_type: Type of event
            description: Event description
            user: User who performed the action
            changes: Dictionary of changes
        """
        audit_log = AuditLog(
            protocol_id=protocol_id,
            event_type=event_type,
            event_description=description,
            user=user,
            changes=changes
        )
        self.session.add(audit_log)

    def search(
        self,
        protocol_id: Optional[str] = None,
        sample_id: Optional[str] = None,
        status: Optional[StatusEnum] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Protocol]:
        """Search protocols with filters.

        Args:
            protocol_id: Protocol ID filter
            sample_id: Sample ID filter
            status: Status filter
            start_date: Start date filter
            end_date: End date filter

        Returns:
            List of matching Protocol instances
        """
        query = self.session.query(Protocol)

        if protocol_id:
            query = query.filter(Protocol.protocol_id == protocol_id)

        if sample_id:
            query = query.filter(Protocol.sample_id.contains(sample_id))

        if status:
            query = query.filter(Protocol.status == status)

        if start_date:
            query = query.filter(Protocol.test_date >= start_date)

        if end_date:
            query = query.filter(Protocol.test_date <= end_date)

        return query.order_by(desc(Protocol.test_date)).all()

    def delete(self, protocol_id: int) -> bool:
        """Delete a protocol.

        Args:
            protocol_id: Protocol ID

        Returns:
            True if deleted, False if not found
        """
        protocol = self.get_by_id(protocol_id)
        if protocol:
            self.session.delete(protocol)
            return True
        return False


class EquipmentRepository:
    """Repository for Equipment operations."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def create(
        self,
        equipment_type: str,
        model: str,
        serial_number: str,
        **kwargs: Any
    ) -> Equipment:
        """Create a new equipment entry.

        Args:
            equipment_type: Type of equipment
            model: Equipment model
            serial_number: Serial number
            **kwargs: Additional equipment attributes

        Returns:
            Created Equipment instance
        """
        equipment = Equipment(
            equipment_type=equipment_type,
            model=model,
            serial_number=serial_number,
            **kwargs
        )
        self.session.add(equipment)
        return equipment

    def get_by_serial(self, serial_number: str) -> Optional[Equipment]:
        """Get equipment by serial number.

        Args:
            serial_number: Equipment serial number

        Returns:
            Equipment instance or None
        """
        return self.session.query(Equipment).filter(
            Equipment.serial_number == serial_number
        ).first()

    def get_all_active(self) -> List[Equipment]:
        """Get all active equipment.

        Returns:
            List of active Equipment instances
        """
        return self.session.query(Equipment).filter(
            Equipment.is_active == True
        ).all()

    def get_calibration_due(self) -> List[Equipment]:
        """Get equipment with calibration due.

        Returns:
            List of Equipment instances with calibration due
        """
        now = datetime.utcnow()
        return self.session.query(Equipment).filter(
            and_(
                Equipment.is_active == True,
                Equipment.next_calibration_date <= now
            )
        ).all()

    def update_calibration(
        self,
        serial_number: str,
        last_calibration_date: datetime,
        next_calibration_date: datetime,
        certificate: str
    ) -> Optional[Equipment]:
        """Update equipment calibration information.

        Args:
            serial_number: Equipment serial number
            last_calibration_date: Last calibration date
            next_calibration_date: Next calibration due date
            certificate: Calibration certificate number

        Returns:
            Updated Equipment instance or None
        """
        equipment = self.get_by_serial(serial_number)
        if equipment:
            equipment.last_calibration_date = last_calibration_date
            equipment.next_calibration_date = next_calibration_date
            equipment.calibration_certificate = certificate
            equipment.calibration_status = "valid"

        return equipment
