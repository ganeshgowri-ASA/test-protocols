"""Tests for test executor."""

import pytest
from uuid import UUID

from src.core.protocol_loader import ProtocolLoader
from src.core.test_executor import TestExecutor
from src.models.test_result import (
    Sample,
    TestStatus,
    PassFailStatus,
    TestStage
)


@pytest.fixture
def protocol():
    """Load VIBR-001 protocol."""
    loader = ProtocolLoader()
    return loader.load_protocol('VIBR-001')


@pytest.fixture
def executor(protocol):
    """Create test executor."""
    return TestExecutor(protocol)


@pytest.fixture
def sample_data():
    """Create sample test data."""
    return [
        Sample(
            sample_id='TEST-001',
            manufacturer='TestCorp',
            model='Model-X',
            serial_number='SN123456'
        ),
        Sample(
            sample_id='TEST-002',
            manufacturer='TestCorp',
            model='Model-X',
            serial_number='SN123457'
        )
    ]


def test_start_session(executor, sample_data):
    """Test starting a test session."""
    session = executor.start_session(
        operator_id='OP001',
        operator_name='John Doe',
        parameters={
            'vibration_severity': 0.5,
            'test_duration': 180,
            'axis': 'vertical'
        },
        samples=sample_data
    )

    assert session is not None
    assert isinstance(session.session_id, UUID)
    assert session.protocol_id == 'VIBR-001'
    assert session.status == TestStatus.IN_PROGRESS
    assert session.operator_name == 'John Doe'
    assert len(session.samples) == 2


def test_start_session_invalid_parameters(executor):
    """Test starting session with invalid parameters."""
    with pytest.raises(ValueError, match="Invalid parameters"):
        executor.start_session(
            operator_id='OP001',
            parameters={
                'vibration_severity': 0.3,  # Below minimum
                'test_duration': 180
            }
        )


def test_add_measurement(executor, sample_data):
    """Test adding measurements."""
    # Start session
    session = executor.start_session(
        operator_id='OP001',
        parameters={'vibration_severity': 0.5, 'test_duration': 180},
        samples=sample_data
    )

    # Add pre-test electrical measurement
    measurement = executor.add_measurement(
        measurement_id='electrical_performance_pre',
        data={
            'Pmax': 300.5,
            'Voc': 45.6,
            'Isc': 8.9,
            'Vmp': 38.2,
            'Imp': 7.86,
            'FF': 75.3
        },
        unit='various',
        operator='OP001'
    )

    assert measurement is not None
    assert measurement.measurement_id == 'electrical_performance_pre'
    assert measurement.stage == TestStage.PRE_TEST
    assert len(session.measurements) == 1


def test_add_measurement_invalid_id(executor, sample_data):
    """Test adding measurement with invalid ID."""
    executor.start_session(
        operator_id='OP001',
        samples=sample_data
    )

    with pytest.raises(ValueError, match="Invalid measurement ID"):
        executor.add_measurement(
            measurement_id='invalid_measurement',
            data={}
        )


def test_add_qc_check(executor, sample_data):
    """Test adding QC check."""
    executor.start_session(
        operator_id='OP001',
        samples=sample_data
    )

    qc_check = executor.add_qc_check(
        check_id='qc_vibration_calibration',
        result=PassFailStatus.PASS,
        details={'calibration_date': '2024-01-01'},
        performed_by='OP001'
    )

    assert qc_check is not None
    assert qc_check.check_id == 'qc_vibration_calibration'
    assert qc_check.result == PassFailStatus.PASS


def test_complete_session(executor, sample_data):
    """Test completing a session."""
    session = executor.start_session(
        operator_id='OP001',
        samples=sample_data
    )

    assert session.status == TestStatus.IN_PROGRESS

    completed_session = executor.complete_session()

    assert completed_session.status == TestStatus.COMPLETED
    assert completed_session.end_time is not None


def test_evaluate_results_power_degradation(executor, sample_data):
    """Test evaluating power degradation criterion."""
    # Start session
    executor.start_session(
        operator_id='OP001',
        samples=sample_data
    )

    # Add pre-test measurement
    executor.add_measurement(
        measurement_id='electrical_performance_pre',
        data={
            'Pmax': 300.0,
            'Voc': 45.0,
            'Isc': 9.0,
            'FF': 74.1
        }
    )

    # Add post-test measurement (3% degradation)
    executor.add_measurement(
        measurement_id='electrical_performance_post',
        data={
            'Pmax': 291.0,
            'Voc': 44.5,
            'Isc': 8.95,
            'FF': 73.0
        }
    )

    # Add visual inspection
    executor.add_measurement(
        measurement_id='visual_inspection_post',
        data={
            'Cell cracks': False,
            'Delamination': False,
            'Glass breakage': False
        }
    )

    # Add insulation resistance
    executor.add_measurement(
        measurement_id='insulation_resistance',
        data={'R_insulation': 50.0}
    )

    # Complete session
    executor.complete_session()

    # Evaluate
    result = executor.evaluate_results()

    assert result.overall_status in [PassFailStatus.PASS, PassFailStatus.FAIL]

    # Check power degradation criterion
    power_eval = next(
        (e for e in result.criterion_evaluations if e.criterion_name == 'power_degradation'),
        None
    )
    assert power_eval is not None
    assert power_eval.measured_value == pytest.approx(3.0, rel=0.1)
    assert power_eval.status == PassFailStatus.PASS  # 3% < 5% limit


def test_evaluate_results_failed_criterion(executor, sample_data):
    """Test evaluation with failed criterion."""
    executor.start_session(
        operator_id='OP001',
        samples=sample_data
    )

    # Add pre-test measurement
    executor.add_measurement(
        measurement_id='electrical_performance_pre',
        data={'Pmax': 300.0, 'Voc': 45.0, 'Isc': 9.0, 'FF': 74.0}
    )

    # Add post-test measurement (8% degradation - exceeds 5% limit)
    executor.add_measurement(
        measurement_id='electrical_performance_post',
        data={'Pmax': 276.0, 'Voc': 44.0, 'Isc': 8.8, 'FF': 71.0}
    )

    # Add visual inspection
    executor.add_measurement(
        measurement_id='visual_inspection_post',
        data={'Cell cracks': False, 'Delamination': False}
    )

    # Add insulation resistance
    executor.add_measurement(
        measurement_id='insulation_resistance',
        data={'R_insulation': 50.0}
    )

    executor.complete_session()

    result = executor.evaluate_results()

    # Should fail due to power degradation
    power_eval = next(
        (e for e in result.criterion_evaluations if e.criterion_name == 'power_degradation'),
        None
    )
    assert power_eval is not None
    assert power_eval.status == PassFailStatus.FAIL


def test_get_session_summary(executor, sample_data):
    """Test getting session summary."""
    executor.start_session(
        operator_id='OP001',
        operator_name='John Doe',
        samples=sample_data
    )

    summary = executor.get_session_summary()

    assert summary['protocol_id'] == 'VIBR-001'
    assert summary['status'] == 'in_progress'
    assert summary['operator'] == 'John Doe'
    assert summary['sample_count'] == 2
    assert summary['measurement_count'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
