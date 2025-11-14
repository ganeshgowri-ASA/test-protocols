"""Integration tests for database operations."""

from datetime import datetime

import pytest

from test_protocols.models.schema import (
    EnvironmentalLog,
    IVMeasurement,
    Protocol,
    TestRun,
    VisualInspection,
)


class TestDatabaseModels:
    """Tests for database models and relationships."""

    def test_create_protocol(self, db_session):
        """Test creating a protocol in database."""
        protocol = Protocol(
            code="TEST-001",
            name="Test Protocol",
            version="1.0.0",
            description="Test protocol description",
            category="Environmental",
            standard="IEC 12345",
            template={"test": "data"},
            active=True,
        )

        db_session.add(protocol)
        db_session.commit()

        # Verify
        retrieved = db_session.query(Protocol).filter_by(code="TEST-001").first()
        assert retrieved is not None
        assert retrieved.name == "Test Protocol"
        assert retrieved.version == "1.0.0"
        assert retrieved.template == {"test": "data"}

    def test_create_test_run(self, db_session):
        """Test creating a test run."""
        # Create protocol first
        protocol = Protocol(
            code="TEST-001",
            name="Test Protocol",
            version="1.0.0",
            description="Test",
            category="Environmental",
            template={},
        )
        db_session.add(protocol)
        db_session.commit()

        # Create test run
        test_run = TestRun(
            protocol_code="TEST-001",
            specimen_id="SPECIMEN-001",
            module_type="Crystalline Silicon",
            manufacturer="Test Mfg",
            rated_power=300.0,
            status="running",
            parameters={"temp": 35.0},
            qc_status="pending",
            operator="Test Operator",
        )

        db_session.add(test_run)
        db_session.commit()

        # Verify
        retrieved = db_session.query(TestRun).filter_by(specimen_id="SPECIMEN-001").first()
        assert retrieved is not None
        assert retrieved.protocol_code == "TEST-001"
        assert retrieved.status == "running"
        assert retrieved.parameters == {"temp": 35.0}

    def test_test_run_protocol_relationship(self, db_session):
        """Test relationship between test run and protocol."""
        protocol = Protocol(
            code="TEST-001",
            name="Test Protocol",
            version="1.0.0",
            description="Test",
            category="Environmental",
            template={},
        )
        db_session.add(protocol)

        test_run = TestRun(
            protocol_code="TEST-001",
            specimen_id="SPECIMEN-001",
            status="running",
            parameters={},
        )
        db_session.add(test_run)
        db_session.commit()

        # Test relationship
        assert test_run.protocol is not None
        assert test_run.protocol.code == "TEST-001"
        assert len(protocol.test_runs) == 1
        assert protocol.test_runs[0].specimen_id == "SPECIMEN-001"

    def test_create_iv_measurement(self, db_session):
        """Test creating I-V measurement."""
        # Setup
        protocol = Protocol(
            code="TEST-001", name="Test", version="1.0.0", description="Test", category="Environmental", template={}
        )
        test_run = TestRun(
            protocol_code="TEST-001",
            specimen_id="SPECIMEN-001",
            status="running",
            parameters={},
        )
        db_session.add(protocol)
        db_session.add(test_run)
        db_session.commit()

        # Create I-V measurement
        iv_measurement = IVMeasurement(
            test_run_id=test_run.id,
            elapsed_hours=0.0,
            voltage=[0, 10, 20, 30, 40],
            current=[8.5, 8.0, 7.0, 4.0, 0],
            power=[0, 80, 140, 120, 0],
            max_power=140.0,
            voc=40.0,
            isc=8.5,
            fill_factor=75.0,
            degradation_percent=0.0,
        )

        db_session.add(iv_measurement)
        db_session.commit()

        # Verify
        retrieved = db_session.query(IVMeasurement).filter_by(test_run_id=test_run.id).first()
        assert retrieved is not None
        assert retrieved.max_power == 140.0
        assert retrieved.voc == 40.0
        assert len(retrieved.voltage) == 5

    def test_create_visual_inspection(self, db_session):
        """Test creating visual inspection."""
        # Setup
        protocol = Protocol(
            code="TEST-001", name="Test", version="1.0.0", description="Test", category="Environmental", template={}
        )
        test_run = TestRun(
            protocol_code="TEST-001",
            specimen_id="SPECIMEN-001",
            status="running",
            parameters={},
        )
        db_session.add(protocol)
        db_session.add(test_run)
        db_session.commit()

        # Create visual inspection
        inspection = VisualInspection(
            test_run_id=test_run.id,
            elapsed_hours=24.0,
            corrosion_rating="1 - Slight corrosion, <1% of area",
            affected_area_percent=0.5,
            notes="Minor corrosion on edges",
        )

        db_session.add(inspection)
        db_session.commit()

        # Verify
        retrieved = db_session.query(VisualInspection).filter_by(test_run_id=test_run.id).first()
        assert retrieved is not None
        assert retrieved.corrosion_rating == "1 - Slight corrosion, <1% of area"
        assert retrieved.affected_area_percent == 0.5

    def test_create_environmental_log(self, db_session):
        """Test creating environmental log."""
        # Setup
        protocol = Protocol(
            code="TEST-001", name="Test", version="1.0.0", description="Test", category="Environmental", template={}
        )
        test_run = TestRun(
            protocol_code="TEST-001",
            specimen_id="SPECIMEN-001",
            status="running",
            parameters={},
        )
        db_session.add(protocol)
        db_session.add(test_run)
        db_session.commit()

        # Create environmental log
        env_log = EnvironmentalLog(
            test_run_id=test_run.id,
            cycle_number=1,
            phase="spray",
            temperature=35.0,
            humidity=95.0,
            salt_concentration=5.0,
            spray_rate=1.5,
            qc_status="pass",
        )

        db_session.add(env_log)
        db_session.commit()

        # Verify
        retrieved = db_session.query(EnvironmentalLog).filter_by(test_run_id=test_run.id).first()
        assert retrieved is not None
        assert retrieved.temperature == 35.0
        assert retrieved.humidity == 95.0
        assert retrieved.qc_status == "pass"

    def test_cascade_delete(self, db_session):
        """Test cascade delete of related records."""
        # Setup
        protocol = Protocol(
            code="TEST-001", name="Test", version="1.0.0", description="Test", category="Environmental", template={}
        )
        test_run = TestRun(
            protocol_code="TEST-001",
            specimen_id="SPECIMEN-001",
            status="running",
            parameters={},
        )
        db_session.add(protocol)
        db_session.add(test_run)
        db_session.commit()

        # Add related records
        iv = IVMeasurement(
            test_run_id=test_run.id,
            elapsed_hours=0.0,
            voltage=[0],
            current=[0],
            power=[0],
            max_power=0,
            voc=0,
            isc=0,
        )
        env = EnvironmentalLog(
            test_run_id=test_run.id,
            temperature=35.0,
            humidity=95.0,
        )

        db_session.add(iv)
        db_session.add(env)
        db_session.commit()

        test_run_id = test_run.id

        # Delete test run
        db_session.delete(test_run)
        db_session.commit()

        # Verify related records are also deleted
        assert db_session.query(IVMeasurement).filter_by(test_run_id=test_run_id).count() == 0
        assert (
            db_session.query(EnvironmentalLog).filter_by(test_run_id=test_run_id).count() == 0
        )
