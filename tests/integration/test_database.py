"""Integration tests for database operations."""

import pytest
from datetime import datetime
from src.database.models import (
    Protocol, TestRun, Measurement, QCResult, Equipment,
    ProtocolStatus, TestRunStatus, QCStatus
)
from src.database.schema import DatabaseManager


class TestDatabaseIntegration:
    """Integration tests for database operations."""

    def test_create_protocol(self, db_manager):
        """Test creating a protocol in the database."""
        session = db_manager.get_session()

        protocol = Protocol(
            id="conc-001",
            name="Concentration Testing",
            version="1.0.0",
            description="Test protocol",
            category="Performance",
            status=ProtocolStatus.ACTIVE,
            schema_json={"test": "schema"},
            created_by="test_user"
        )

        session.add(protocol)
        session.commit()

        # Verify
        retrieved = session.query(Protocol).filter_by(id="conc-001").first()
        assert retrieved is not None
        assert retrieved.name == "Concentration Testing"
        assert retrieved.version == "1.0.0"

        session.close()

    def test_create_equipment(self, db_manager):
        """Test creating equipment record."""
        session = db_manager.get_session()

        equipment = Equipment(
            id="SIM-001",
            name="Solar Simulator 1",
            equipment_type="solar_simulator",
            manufacturer="TestCorp",
            calibration_date=datetime.now(),
            calibration_status="valid"
        )

        session.add(equipment)
        session.commit()

        # Verify
        retrieved = session.query(Equipment).filter_by(id="SIM-001").first()
        assert retrieved is not None
        assert retrieved.equipment_type == "solar_simulator"

        session.close()

    def test_create_test_run(self, db_manager):
        """Test creating a test run with measurements."""
        session = db_manager.get_session()

        # Create protocol first
        protocol = Protocol(
            id="conc-001",
            name="Test Protocol",
            version="1.0.0",
            schema_json={},
            status=ProtocolStatus.ACTIVE
        )
        session.add(protocol)

        # Create equipment
        equipment = Equipment(
            id="SIM-001",
            name="Simulator",
            equipment_type="solar_simulator",
            calibration_status="valid"
        )
        session.add(equipment)

        # Create test run
        test_run = TestRun(
            id="CONC-001-20251114-0001",
            protocol_id="conc-001",
            equipment_id="SIM-001",
            sample_id="PV-SAMPLE-001",
            operator="Test Operator",
            status=TestRunStatus.COMPLETED,
            started_at=datetime.now(),
            completed_at=datetime.now()
        )
        session.add(test_run)

        session.commit()

        # Verify
        retrieved = session.query(TestRun).filter_by(id="CONC-001-20251114-0001").first()
        assert retrieved is not None
        assert retrieved.sample_id == "PV-SAMPLE-001"
        assert retrieved.protocol.id == "conc-001"
        assert retrieved.equipment.id == "SIM-001"

        session.close()

    def test_create_measurements(self, db_manager):
        """Test creating measurements for a test run."""
        session = db_manager.get_session()

        # Create prerequisite records
        protocol = Protocol(
            id="conc-001",
            name="Test",
            version="1.0.0",
            schema_json={},
            status=ProtocolStatus.ACTIVE
        )
        session.add(protocol)

        test_run = TestRun(
            id="TEST-001",
            protocol_id="conc-001",
            sample_id="SAMPLE-001",
            operator="Test",
            status=TestRunStatus.IN_PROGRESS
        )
        session.add(test_run)

        # Create measurements
        measurement1 = Measurement(
            test_run_id="TEST-001",
            sequence_number=1,
            concentration_suns=1.0,
            temperature_c=25.0,
            voc=0.650,
            isc=8.5,
            vmp=0.550,
            imp=8.0,
            fill_factor=0.846,
            efficiency=22.5
        )

        measurement2 = Measurement(
            test_run_id="TEST-001",
            sequence_number=2,
            concentration_suns=10.0,
            temperature_c=25.0,
            voc=0.750,
            isc=85.0,
            vmp=0.650,
            imp=80.0,
            fill_factor=0.815,
            efficiency=26.8
        )

        session.add_all([measurement1, measurement2])
        session.commit()

        # Verify
        measurements = session.query(Measurement).filter_by(test_run_id="TEST-001").all()
        assert len(measurements) == 2
        assert measurements[0].concentration_suns == 1.0
        assert measurements[1].concentration_suns == 10.0

        session.close()

    def test_create_qc_results(self, db_manager):
        """Test creating QC results."""
        session = db_manager.get_session()

        # Create prerequisite records
        protocol = Protocol(
            id="conc-001",
            name="Test",
            version="1.0.0",
            schema_json={},
            status=ProtocolStatus.ACTIVE
        )
        session.add(protocol)

        test_run = TestRun(
            id="TEST-001",
            protocol_id="conc-001",
            sample_id="SAMPLE-001",
            operator="Test",
            status=TestRunStatus.COMPLETED
        )
        session.add(test_run)

        # Create QC results
        qc_result = QCResult(
            test_run_id="TEST-001",
            criterion_name="fill_factor_minimum",
            criterion_description="Minimum fill factor requirement",
            status=QCStatus.PASS,
            measured_value=0.846,
            expected_value=0.65,
            checked_by="test_user"
        )

        session.add(qc_result)
        session.commit()

        # Verify
        retrieved = session.query(QCResult).filter_by(test_run_id="TEST-001").first()
        assert retrieved is not None
        assert retrieved.status == QCStatus.PASS
        assert retrieved.measured_value == 0.846

        session.close()

    def test_cascade_delete(self, db_manager):
        """Test cascade deletion of related records."""
        session = db_manager.get_session()

        # Create protocol and test run with measurements
        protocol = Protocol(
            id="conc-001",
            name="Test",
            version="1.0.0",
            schema_json={},
            status=ProtocolStatus.ACTIVE
        )
        session.add(protocol)

        test_run = TestRun(
            id="TEST-001",
            protocol_id="conc-001",
            sample_id="SAMPLE-001",
            operator="Test",
            status=TestRunStatus.COMPLETED
        )
        session.add(test_run)

        measurement = Measurement(
            test_run_id="TEST-001",
            sequence_number=1,
            concentration_suns=1.0,
            temperature_c=25.0,
            efficiency=22.5
        )
        session.add(measurement)

        session.commit()

        # Delete test run
        session.delete(test_run)
        session.commit()

        # Measurements should be deleted too (cascade)
        remaining_measurements = session.query(Measurement).filter_by(
            test_run_id="TEST-001"
        ).all()
        assert len(remaining_measurements) == 0

        session.close()
