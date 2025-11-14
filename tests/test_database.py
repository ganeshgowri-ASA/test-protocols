"""
Database Tests
Tests for database models and operations
"""

import pytest
from datetime import datetime
from database.models import Protocol, TestRun, DataPoint, QCResult, InterimTest
from database.models import ProtocolStatus, TestRunStatus


class TestProtocolModel:
    """Test Protocol model"""

    def test_create_protocol(self, test_db_session, desert_protocol_data):
        """Test creating a protocol"""
        protocol = Protocol(
            id=desert_protocol_data['metadata']['id'],
            protocol_number=desert_protocol_data['metadata']['protocol_number'],
            name=desert_protocol_data['metadata']['name'],
            category=desert_protocol_data['metadata']['category'],
            subcategory=desert_protocol_data['metadata'].get('subcategory'),
            version=desert_protocol_data['metadata']['version'],
            description=desert_protocol_data['metadata']['description'],
            status=ProtocolStatus.ACTIVE,
            definition=desert_protocol_data
        )

        test_db_session.add(protocol)
        test_db_session.commit()

        assert protocol.id == "DESERT-001"
        assert protocol.name == "Desert Climate Test"

    def test_query_protocol(self, test_db_session, sample_protocol):
        """Test querying protocols"""
        protocol = test_db_session.query(Protocol).filter_by(id="DESERT-001").first()

        assert protocol is not None
        assert protocol.name == "Desert Climate Test"
        assert protocol.category == "Environmental"

    def test_protocol_relationships(self, test_db_session, sample_protocol, sample_test_run):
        """Test protocol relationships"""
        protocol = test_db_session.query(Protocol).filter_by(id="DESERT-001").first()

        assert len(protocol.test_runs) > 0
        assert protocol.test_runs[0].id == "test-run-001"


class TestTestRunModel:
    """Test TestRun model"""

    def test_create_test_run(self, test_db_session, sample_protocol):
        """Test creating a test run"""
        test_run = TestRun(
            id="test-001",
            protocol_id=sample_protocol.id,
            module_serial_number="MOD-001",
            batch_id="BATCH-001",
            operator="operator1",
            status=TestRunStatus.PENDING,
            start_time=datetime.utcnow(),
            total_cycles=200
        )

        test_db_session.add(test_run)
        test_db_session.commit()

        assert test_run.id == "test-001"
        assert test_run.protocol_id == "DESERT-001"

    def test_query_test_run(self, test_db_session, sample_test_run):
        """Test querying test runs"""
        test_run = test_db_session.query(TestRun).filter_by(id="test-run-001").first()

        assert test_run is not None
        assert test_run.module_serial_number == "MOD-12345"

    def test_test_run_status_updates(self, test_db_session, sample_test_run):
        """Test updating test run status"""
        test_run = test_db_session.query(TestRun).filter_by(id="test-run-001").first()

        test_run.status = TestRunStatus.RUNNING
        test_db_session.commit()

        updated = test_db_session.query(TestRun).filter_by(id="test-run-001").first()
        assert updated.status == TestRunStatus.RUNNING


class TestDataPointModel:
    """Test DataPoint model"""

    def test_create_data_point(self, test_db_session, sample_test_run):
        """Test creating a data point"""
        data_point = DataPoint(
            test_run_id=sample_test_run.id,
            timestamp=datetime.utcnow(),
            cycle_number=1,
            phase="daytime",
            chamber_temperature=65.0,
            chamber_humidity=15.0,
            module_temperature=75.0,
            voc=45.6,
            isc=9.8,
            pmax=342.2
        )

        test_db_session.add(data_point)
        test_db_session.commit()

        assert data_point.id is not None
        assert data_point.chamber_temperature == 65.0

    def test_query_data_points(self, test_db_session, sample_test_run):
        """Test querying data points"""
        # Create multiple data points
        for i in range(5):
            dp = DataPoint(
                test_run_id=sample_test_run.id,
                timestamp=datetime.utcnow(),
                cycle_number=i,
                chamber_temperature=65.0 + i
            )
            test_db_session.add(dp)

        test_db_session.commit()

        data_points = test_db_session.query(DataPoint).filter_by(
            test_run_id=sample_test_run.id
        ).all()

        assert len(data_points) == 5

    def test_data_point_relationships(self, test_db_session, sample_test_run):
        """Test data point relationships"""
        dp = DataPoint(
            test_run_id=sample_test_run.id,
            timestamp=datetime.utcnow(),
            chamber_temperature=65.0
        )

        test_db_session.add(dp)
        test_db_session.commit()

        assert dp.test_run is not None
        assert dp.test_run.id == sample_test_run.id


class TestQCResultModel:
    """Test QCResult model"""

    def test_create_qc_result(self, test_db_session, sample_test_run):
        """Test creating a QC result"""
        qc_result = QCResult(
            test_run_id=sample_test_run.id,
            check_name="temperature_stability",
            check_type="continuous",
            timestamp=datetime.utcnow(),
            cycle_number=1,
            passed=True,
            severity="major",
            measured_value=65.0,
            threshold_value=2.0
        )

        test_db_session.add(qc_result)
        test_db_session.commit()

        assert qc_result.id is not None
        assert qc_result.passed is True

    def test_query_qc_results(self, test_db_session, sample_test_run):
        """Test querying QC results"""
        # Create multiple QC results
        for i in range(3):
            qc = QCResult(
                test_run_id=sample_test_run.id,
                check_name=f"check_{i}",
                timestamp=datetime.utcnow(),
                passed=i % 2 == 0
            )
            test_db_session.add(qc)

        test_db_session.commit()

        passed_checks = test_db_session.query(QCResult).filter_by(
            test_run_id=sample_test_run.id,
            passed=True
        ).count()

        assert passed_checks == 2


class TestInterimTestModel:
    """Test InterimTest model"""

    def test_create_interim_test(self, test_db_session, sample_test_run):
        """Test creating an interim test"""
        interim_test = InterimTest(
            test_run_id=sample_test_run.id,
            cycle_number=50,
            test_type="iv_curve",
            timestamp=datetime.utcnow(),
            voc=45.3,
            isc=9.75,
            pmax=338.5,
            power_retention_percent=98.9,
            degradation_percent=1.1,
            passed=True
        )

        test_db_session.add(interim_test)
        test_db_session.commit()

        assert interim_test.id is not None
        assert interim_test.cycle_number == 50

    def test_query_interim_tests(self, test_db_session, sample_test_run):
        """Test querying interim tests"""
        # Create interim tests at different cycles
        for cycle in [50, 100, 150, 200]:
            it = InterimTest(
                test_run_id=sample_test_run.id,
                cycle_number=cycle,
                test_type="iv_curve",
                timestamp=datetime.utcnow(),
                pmax=342.2 - (cycle * 0.07)  # Simulated degradation
            )
            test_db_session.add(it)

        test_db_session.commit()

        interim_tests = test_db_session.query(InterimTest).filter_by(
            test_run_id=sample_test_run.id
        ).order_by(InterimTest.cycle_number).all()

        assert len(interim_tests) == 4
        assert interim_tests[0].cycle_number == 50
        assert interim_tests[-1].cycle_number == 200
