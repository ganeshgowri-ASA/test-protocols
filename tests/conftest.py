"""Pytest configuration and fixtures."""

import pytest
import os
from pathlib import Path
from datetime import datetime
import tempfile

from src.utils.db import DatabaseManager
from src.core.protocol import ProtocolConfig
from src.tests.track.track_001.protocol import TRACK001Protocol


@pytest.fixture(scope="session")
def test_db():
    """Create a test database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db_manager = DatabaseManager({
            'database': {
                'url': f'sqlite:///{db_path}',
                'echo': False
            }
        })

        # Initialize schema
        schema_file = 'data/db/schema.sql'
        if Path(schema_file).exists():
            db_manager.init_database(schema_file)

        yield db_manager


@pytest.fixture
def sample_protocol_config():
    """Sample protocol configuration for testing."""
    return ProtocolConfig(
        protocol_id="TEST-001",
        name="Test Protocol",
        version="1.0.0",
        category="Performance",
        test_parameters={
            'duration': {'value': 1, 'unit': 'hours'},
            'sample_interval': {'value': 5, 'unit': 'minutes'},
            'metrics': [
                {
                    'name': 'test_metric',
                    'type': 'angle',
                    'unit': 'degrees',
                    'description': 'Test metric'
                }
            ]
        },
        qc_criteria={
            'data_completeness': 95,
            'limits': {'max_value': 100}
        },
        analysis_methods={
            'statistical_analysis': {
                'methods': ['mean', 'std_dev'],
                'parameters': ['test_metric']
            }
        },
        description="Test protocol configuration",
        metadata={
            'author': 'Test Suite',
            'created_date': datetime.now().isoformat()
        }
    )


@pytest.fixture
def track001_config():
    """TRACK-001 protocol configuration for testing."""
    return ProtocolConfig(
        protocol_id="TRACK-001",
        name="Tracker Performance Test",
        version="1.0.0",
        category="Performance",
        test_parameters={
            'duration': {'value': 1, 'unit': 'hours'},
            'sample_interval': {'value': 5, 'unit': 'minutes'},
            'metrics': [
                {
                    'name': 'azimuth_angle',
                    'type': 'angle',
                    'unit': 'degrees',
                    'description': 'Horizontal tracking angle'
                },
                {
                    'name': 'elevation_angle',
                    'type': 'angle',
                    'unit': 'degrees',
                    'description': 'Vertical tracking angle'
                },
                {
                    'name': 'tracking_error',
                    'type': 'angle',
                    'unit': 'degrees',
                    'description': 'Deviation from ideal sun position'
                }
            ],
            'tracking_mode': 'dual_axis',
            'performance_metrics': {
                'tracking_accuracy': {
                    'measurement_points': 100,
                    'acceptance_threshold': 2.0,
                    'unit': 'degrees'
                }
            }
        },
        qc_criteria={
            'tracking_accuracy': {
                'max_error': 2.0,
                'unit': 'degrees'
            },
            'data_completeness': 95
        },
        analysis_methods={
            'statistical_analysis': {
                'methods': ['mean', 'median', 'std_dev', 'percentile_95'],
                'parameters': ['tracking_error']
            }
        },
        description="Tracker performance test",
        metadata={'author': 'Test Suite'}
    )


@pytest.fixture
def sample_measurements():
    """Sample measurement data for testing."""
    base_time = datetime.now()

    measurements = []
    for i in range(10):
        timestamp = base_time.replace(minute=i * 5)

        measurements.extend([
            {
                'run_id': 'TEST-RUN-001',
                'timestamp': timestamp,
                'metric_name': 'test_metric',
                'metric_value': 45.0 + i * 0.5,
                'metric_unit': 'degrees',
                'quality_flag': 'good'
            }
        ])

    return measurements
